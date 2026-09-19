"""Tests for /api/enquiries and /api/admin/enquiries."""
import os
import time
import uuid
import requests
import pytest

BASE_URL = "https://515dc9a7-0d61-46f2-bb41-31805466b8fc.preview.emergentagent.com"
ADMIN_TOKEN = "nova-newsroom-4f1c8b2ad96e47"

TAG = f"TEST_{uuid.uuid4().hex[:8]}"


def _payload(**over):
    p = {
        "fullname": f"{TAG} John Doe",
        "email": "test+nova@example.com",
        "code": "90",
        "phone": "533 000 0000",
        "project": "East West",
        "source": "Instagram",
        "comments": "Please contact me.",
        "news": True,
        "privacy": True,
        "page": "index.html",
    }
    p.update(over)
    return p


def test_valid_submission_returns_202():
    r = requests.post(f"{BASE_URL}/api/enquiries", json=_payload(), timeout=15)
    assert r.status_code == 202, r.text
    body = r.json()
    assert body.get("ok") is True
    assert "id" in body


def test_privacy_false_returns_422():
    r = requests.post(f"{BASE_URL}/api/enquiries", json=_payload(privacy=False), timeout=15)
    assert r.status_code == 422


def test_short_fullname_returns_422():
    r = requests.post(f"{BASE_URL}/api/enquiries", json=_payload(fullname="A"), timeout=15)
    assert r.status_code == 422


def test_bad_email_returns_422():
    r = requests.post(f"{BASE_URL}/api/enquiries", json=_payload(email="not-an-email"), timeout=15)
    assert r.status_code == 422


def test_crlf_injection_returns_422():
    r = requests.post(f"{BASE_URL}/api/enquiries", json=_payload(fullname="Foo\r\nBcc: x@y.z"), timeout=15)
    assert r.status_code == 422
    r2 = requests.post(f"{BASE_URL}/api/enquiries", json=_payload(project="A\nB"), timeout=15)
    assert r2.status_code == 422


def test_honeypot_returns_202_but_no_record():
    hp_fullname = f"{TAG}_HONEYPOT"
    r = requests.post(f"{BASE_URL}/api/enquiries", json=_payload(fullname=hp_fullname, website="spam"), timeout=15)
    assert r.status_code == 202
    # verify no record stored with that fullname
    time.sleep(1)
    r2 = requests.get(f"{BASE_URL}/api/admin/enquiries", headers={"X-Admin-Token": ADMIN_TOKEN}, timeout=15)
    assert r2.status_code == 200
    items = r2.json().get("items", [])
    assert not any(it.get("fullname") == hp_fullname for it in items)


def test_turkish_chars_roundtrip():
    name = f"{TAG} İsmail Şükrü Öz Ğül Çil Ünsal"
    comment = "Merhaba İstanbul — şğçüö"
    r = requests.post(f"{BASE_URL}/api/enquiries", json=_payload(fullname=name, comments=comment), timeout=15)
    assert r.status_code == 202
    doc_id = r.json()["id"]
    time.sleep(1)
    r2 = requests.get(f"{BASE_URL}/api/admin/enquiries", headers={"X-Admin-Token": ADMIN_TOKEN}, timeout=15)
    assert r2.status_code == 200
    found = next((it for it in r2.json()["items"] if it.get("id") == doc_id), None)
    assert found is not None
    assert found["fullname"] == name
    assert found["comments"] == comment


def test_admin_requires_token():
    r = requests.get(f"{BASE_URL}/api/admin/enquiries", timeout=15)
    assert r.status_code == 401
    r2 = requests.get(f"{BASE_URL}/api/admin/enquiries", headers={"X-Admin-Token": "wrong"}, timeout=15)
    assert r2.status_code == 401


def test_admin_returns_items_newest_first_and_email_status():
    r = requests.get(f"{BASE_URL}/api/admin/enquiries", headers={"X-Admin-Token": ADMIN_TOKEN}, timeout=15)
    assert r.status_code == 200
    items = r.json()["items"]
    assert isinstance(items, list) and items
    ts = [it["created_at"] for it in items]
    assert ts == sorted(ts, reverse=True)
    # email_status should be smtp_not_configured (SMTP intentionally empty)
    latest = items[0]
    assert latest.get("email_status") in {"smtp_not_configured", "queued"}
    # No SMTP password leak
    txt = r.text.lower()
    assert "smtp_password" not in txt
    assert "password" not in {k.lower() for k in latest.keys()}


def test_rate_limit_returns_429_on_sixth():
    # Use unique IP via X-Forwarded-For
    ip = f"10.20.30.{uuid.uuid4().int % 250 + 1}"
    headers = {"X-Forwarded-For": ip}
    codes = []
    for i in range(6):
        r = requests.post(f"{BASE_URL}/api/enquiries", json=_payload(fullname=f"{TAG} RL {i}"), headers=headers, timeout=15)
        codes.append(r.status_code)
    assert codes[:5] == [202] * 5, codes
    assert codes[5] == 429, codes
