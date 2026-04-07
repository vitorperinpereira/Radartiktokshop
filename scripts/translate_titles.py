import httpx
import asyncio
from sqlalchemy import select
from services.shared.config import get_settings
from services.shared.db.session import build_session_factory
from services.shared.db.models import Product

def translate_text(text):
    if not text:
        return text
    import urllib.parse
    url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=pt&dt=t&q=" + urllib.parse.quote(text)
    try:
        r = httpx.get(url, timeout=5)
        if r.status_code == 200:
            return "".join([t[0] for t in r.json()[0]])
        return text
    except:
        return text

def translate_all():
    sf = build_session_factory(settings=get_settings())
    with sf() as session:
        products = session.execute(select(Product)).scalars().all()
        for p in products:
            if not p.title: continue
            pt_words = ["para", "com", "mulher", "homem", "bolsa", "luminaria", "aposta", "kit", "massageador", "e"]
            if sum(1 for w in pt_words if w in p.title.lower().split()) >= 2:
                continue
            translated = translate_text(p.title)
            if translated and translated != p.title:
                p.title = translated
        session.commit()
    print("Traduzido todos os products")

if __name__ == "__main__":
    translate_all()
