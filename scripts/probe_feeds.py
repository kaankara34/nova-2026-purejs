"""One-off probe: which candidate feeds actually work (status, items, recent dates)."""
import asyncio
import sys

import httpx
from defusedxml import ElementTree as ET

UA = "NovaKonutNewsroomBot/1.0 (+https://nova.istanbul; newsroom aggregation)"

CANDIDATES = [
    ("resmigazete-mevzuat", "https://www.resmigazete.gov.tr/rss/mevzuat.rss"),
    ("resmigazete-ilan", "https://www.resmigazete.gov.tr/rss/ilan.rss"),
    ("resmigazete-feed", "https://www.resmigazete.gov.tr/feed"),
    ("csb", "https://csb.gov.tr/rss/haberler"),
    ("csb2", "https://www.csb.gov.tr/rss"),
    ("ibb-haber", "https://www.ibb.istanbul/rss/haberler"),
    ("ibb2", "https://www.ibb.istanbul/haberler/rss"),
    ("kadikoy-bel", "https://www.kadikoy.bel.tr/rss"),
    ("kadikoy-bel2", "https://www.kadikoy.bel.tr/feed"),
    ("kadikoy-bel3", "https://www.kadikoy.bel.tr/rss.xml"),
    ("kiptas", "https://www.kiptas.istanbul/rss"),
    ("afad", "https://www.afad.gov.tr/rss"),
    ("tuik", "https://data.tuik.gov.tr/Bulten/Rss"),
    ("imo", "https://www.imo.org.tr/rss.xml"),
    ("mo", "https://www.mo.org.tr/rss.xml"),
    ("mimarizm", "https://www.mimarizm.com/rss"),
    ("yapidergisi", "https://www.yapidergisi.com/feed"),
    ("dunya-ekonomi", "https://www.dunya.com/rss?dunya"),
    ("dunya-sektorler", "https://www.dunya.com/rss?sektorler"),
    ("ekonomim", "https://www.ekonomim.com/rss"),
    ("bloomberght", "https://www.bloomberght.com/rss"),
    ("aa-turkiye", "https://www.aa.com.tr/tr/rss/default?cat=turkiye"),
    ("aa-yasam", "https://www.aa.com.tr/tr/rss/default?cat=yasam"),
    ("emlakhaberleri", "https://emlakkulisi.com/rss"),
    ("construction-dive", "https://www.constructiondive.com/feeds/news/"),
    ("enr", "https://www.enr.com/rss/all-news"),
    ("riba", "https://www.architecture.com/rss/news"),
    ("architects-journal", "https://www.architectsjournal.co.uk/feed"),
    ("bdonline", "https://www.bdonline.co.uk/feed"),
    ("dezeen-arch", "https://www.dezeen.com/architecture/feed/"),
    ("worldarch", "https://worldarchitecture.org/rss/architecture-news.xml"),
    ("archinect", "https://archinect.com/feed/1/news"),
    ("artnews", "https://www.artnews.com/feed/"),
    ("artforum", "https://www.artforum.com/feed/"),
    ("thegreatart", "https://www.theartnewspaper.com/rss"),
    ("apollo", "https://apollo-magazine.com/feed/"),
    ("smithsonian-art", "https://www.smithsonianmag.com/rss/arts-culture/"),
    ("guardian-cities", "https://www.theguardian.com/cities/rss"),
    ("citylab", "https://www.bloomberg.com/feeds/citylab.rss"),
    ("nextcity", "https://nextcity.org/rss"),
    ("phaidon", "https://www.phaidon.com/agenda/rss/"),
    ("gaz-arkitera", "https://www.arkitera.com/feed/"),
    ("arkiv", "https://www.arkiv.com.tr/feed"),
    ("yapikatalogu", "https://www.yapikatalogu.com/rss"),
    ("insaatdunyasi", "https://www.insaatdunyasi.com.tr/feed"),
    ("tmb", "https://www.tmb.org.tr/rss"),
    ("imsad", "https://www.imsad.org/rss"),
    ("gyoder", "https://www.gyoder.org.tr/rss"),
    ("konutder", "https://konutder.org.tr/feed/"),
    ("kentselstrateji", "https://kentselstrateji.com/feed/"),
    ("hurriyet-emlak", "https://www.hurriyet.com.tr/rss/emlak"),
    ("milliyet-emlak", "https://www.milliyet.com.tr/rss/rssnew/emlakrss.xml"),
    ("sozcu-emlak", "https://www.sozcu.com.tr/feeds-rss-category-ekonomi"),
    ("ntv-ekonomi", "https://www.ntv.com.tr/ekonomi.rss"),
    ("trthaber-ekonomi", "https://www.trthaber.com/ekonomi_articles.rss"),
    ("trthaber-kultur", "https://www.trthaber.com/kultur_sanat_articles.rss"),
    ("aa-kultur", "https://www.aa.com.tr/tr/rss/default?cat=kultur"),
    ("aa-analiz", "https://www.aa.com.tr/tr/rss/default?cat=analiz"),
    ("istanbulmodern", "https://www.istanbulmodern.org/rss"),
    ("saltonline", "https://saltonline.org/rss"),
    ("iksv", "https://www.iksv.org/rss"),
    ("pera", "https://www.peramuzesi.org.tr/rss"),
    ("hyperallergic", "https://hyperallergic.com/feed/"),
]


async def probe(client, key, url):
    try:
        res = await client.get(url, headers={"User-Agent": UA, "Accept": "application/rss+xml,application/xml,text/xml;q=0.9,*/*;q=0.5"})
    except Exception as exc:
        return key, url, f"ERR {type(exc).__name__}", 0
    if res.status_code != 200:
        return key, url, f"HTTP {res.status_code}", 0
    body = res.content.lstrip()
    try:
        root = ET.fromstring(body, forbid_dtd=False, forbid_entities=True, forbid_external=True)
    except Exception as exc:
        return key, url, f"NOTXML {type(exc).__name__}", 0
    n = len(list(root.iter("item"))) + len(list(root.iter("{http://www.w3.org/2005/Atom}entry")))
    return key, url, ("OK" if n else "EMPTY"), n


async def main():
    async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
        results = await asyncio.gather(*(probe(client, k, u) for k, u in CANDIDATES))
    for key, url, status, n in results:
        if status == "OK":
            print(f"OK   {n:4d}  {key:24s} {url}")
    print("---- failures ----", file=sys.stderr)
    for key, url, status, _ in results:
        if status != "OK":
            print(f"{status:22s} {key:24s} {url}", file=sys.stderr)


asyncio.run(main())
