"""Register-interest / contact form submissions: persisted to Mongo, emailed over SMTP."""
import logging
import os
import re
import time
from datetime import datetime, timezone
from email.message import EmailMessage
from email.policy import SMTP as SMTP_POLICY

import aiosmtplib
from fastapi import APIRouter, BackgroundTasks, Header, HTTPException, Request, status
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, EmailStr, Field, field_validator

log = logging.getLogger("nova.enquiries")

router = APIRouter(prefix="/api")

_client = AsyncIOMotorClient(os.environ["MONGO_URL"])
_db = _client[os.environ["DB_NAME"]]
enquiries = _db["enquiries"]
_rate = _db["enquiry_rate_limits"]

MAIL_TO = os.environ["MAIL_TO"]
RATE_LIMIT_PER_MINUTE = 5

PHONE_RE = re.compile(r"^[0-9 ()+\-./]{0,32}$")


class Enquiry(BaseModel):
    fullname: str = Field(min_length=2, max_length=120)
    email: EmailStr
    code: str = Field(default="", max_length=8)
    phone: str = Field(default="", max_length=32)
    project: str = Field(default="", max_length=120)
    source: str = Field(default="", max_length=120)
    comments: str = Field(default="", max_length=4000)
    news: bool = False
    privacy: bool = False
    page: str = Field(default="", max_length=200)
    # hidden honeypot, must stay empty
    website: str = Field(default="", max_length=200)

    @field_validator("fullname", "code", "phone", "project", "source", "page", "website")
    @classmethod
    def single_line(cls, v: str) -> str:
        if "\r" in v or "\n" in v:
            raise ValueError("line breaks are not allowed")
        return v.strip()

    @field_validator("comments")
    @classmethod
    def trim_comments(cls, v: str) -> str:
        return v.strip()

    @field_validator("phone")
    @classmethod
    def phone_shape(cls, v: str) -> str:
        if v and not PHONE_RE.match(v):
            raise ValueError("invalid phone number")
        return v

    @field_validator("privacy")
    @classmethod
    def privacy_required(cls, v: bool) -> bool:
        if not v:
            raise ValueError("privacy policy must be accepted")
        return v


def _smtp_config():
    host = os.environ.get("SMTP_HOST", "").strip()
    if not host:
        return None
    security = os.environ.get("SMTP_SECURITY", "starttls").strip().lower()
    if security not in {"starttls", "ssl"}:
        log.error("SMTP_SECURITY must be starttls or ssl, got %r", security)
        return None
    return {
        "hostname": host,
        "port": int(os.environ.get("SMTP_PORT", "587")),
        "username": os.environ.get("SMTP_USERNAME", "").strip() or None,
        "password": os.environ.get("SMTP_PASSWORD", "") or None,
        "security": security,
        "sender": os.environ.get("MAIL_FROM", "").strip() or os.environ.get("SMTP_USERNAME", "").strip(),
    }


def _build_message(doc: dict, cfg: dict) -> EmailMessage:
    msg = EmailMessage(policy=SMTP_POLICY)
    msg["From"] = cfg["sender"]
    msg["To"] = MAIL_TO
    msg["Reply-To"] = doc["email"]
    msg["Subject"] = f"Register Interest — {doc['fullname']}"
    phone = f"+{doc['code']} {doc['phone']}".strip() if doc.get("code") else doc.get("phone", "")
    lines = [
        f"Name: {doc['fullname']}",
        f"Email: {doc['email']}",
        f"Phone: {phone or '—'}",
        f"Project: {doc.get('project') or '—'}",
        f"How they heard of us: {doc.get('source') or '—'}",
        f"Marketing consent: {'yes' if doc.get('news') else 'no'}",
        f"Submitted from: {doc.get('page') or '—'}",
        f"Received: {doc['created_at']}",
    ]
    if doc.get("comments"):
        lines += ["", "Message:", doc["comments"]]
    msg.set_content("\n".join(lines) + "\n", subtype="plain", charset="utf-8")
    return msg


async def _deliver(doc_id: str, doc: dict) -> None:
    cfg = _smtp_config()
    if not cfg:
        await enquiries.update_one({"id": doc_id}, {"$set": {"email_status": "smtp_not_configured"}})
        log.warning("Enquiry %s stored but SMTP is not configured", doc_id)
        return
    try:
        kwargs = {
            "hostname": cfg["hostname"],
            "port": cfg["port"],
            "timeout": 20,
            "validate_certs": True,
        }
        if cfg["username"]:
            kwargs["username"] = cfg["username"]
            kwargs["password"] = cfg["password"]
        if cfg["security"] == "ssl":
            kwargs.update(use_tls=True, start_tls=False)
        else:
            kwargs.update(use_tls=False, start_tls=True)
        await aiosmtplib.send(_build_message(doc, cfg), **kwargs)
        await enquiries.update_one({"id": doc_id}, {"$set": {"email_status": "sent"}})
    except Exception as exc:
        log.exception("SMTP delivery failed for enquiry %s", doc_id)
        await enquiries.update_one(
            {"id": doc_id},
            {"$set": {"email_status": "failed", "email_error": type(exc).__name__}},
        )


async def _allow(ip: str) -> bool:
    key = f"{ip}:{int(time.time() // 60)}"
    doc = await _rate.find_one_and_update(
        {"_id": key},
        {"$inc": {"count": 1}, "$setOnInsert": {"created_at": datetime.now(timezone.utc)}},
        upsert=True,
        return_document=True,
    )
    return doc["count"] <= RATE_LIMIT_PER_MINUTE


@router.post("/enquiries", status_code=status.HTTP_202_ACCEPTED)
async def create_enquiry(payload: Enquiry, request: Request, background: BackgroundTasks):
    if payload.website:
        return {"ok": True}
    ip = request.headers.get("x-forwarded-for", "").split(",")[0].strip() or (
        request.client.host if request.client else "unknown"
    )
    if not await _allow(ip):
        raise HTTPException(status_code=429, detail="Too many submissions, please try again shortly.")

    import uuid

    doc_id = str(uuid.uuid4())
    doc = payload.model_dump(exclude={"website"})
    doc.update(
        {
            "id": doc_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "email_status": "queued",
        }
    )
    await enquiries.insert_one(dict(doc))
    background.add_task(_deliver, doc_id, doc)
    return {"ok": True, "id": doc_id}


@router.get("/admin/enquiries")
async def list_enquiries(x_admin_token: str = Header(default="")):
    expected = os.environ.get("NEWS_ADMIN_TOKEN", "")
    if not expected or x_admin_token != expected:
        raise HTTPException(status_code=401, detail="Unauthorised")
    cursor = enquiries.find({}, {"_id": 0}).sort("created_at", -1).limit(200)
    return {"items": await cursor.to_list(length=200)}
