import json
import uuid
from decimal import Decimal
from datetime import datetime, timezone
from sqlalchemy import select
from services.shared.config import get_settings
from services.shared.db.session import build_session_factory
from services.shared.db.models import Base, Report

sf = build_session_factory(settings=get_settings())
session = sf()

latest_report = session.execute(select(Report).order_by(Report.created_at.desc()).limit(1)).scalar_one_or_none()
if not latest_report:
    print('No report found')
    exit(1)

payload = latest_report.report_payload or {}
items = payload.get('entries') or payload.get('items') or []

if not items:
    print('No items in payload')
    exit(1)

base_items = list(items)
new_items = []
images = [
    'https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=400&q=80',
    'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=400&q=80',
    'https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=400&q=80',
    'https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?auto=format&fit=crop&w=400&q=80',
    'https://images.unsplash.com/photo-1583394838336-acd977736f90?auto=format&fit=crop&w=400&q=80',
    'https://images.unsplash.com/photo-1560343090-f0409e92791a?auto=format&fit=crop&w=400&q=80',
    'https://images.unsplash.com/photo-1608042314453-ae338d80c427?auto=format&fit=crop&w=400&q=80',
    'https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?auto=format&fit=crop&w=400&q=80'
]

for i in range(75):
    base = base_items[i % len(base_items)].copy()
    base['product_id'] = str(uuid.uuid4())
    base['rank'] = i + 1
    base['name'] = f"{base.get('name', 'Product')} Variant V{i+1}"
    base['final_score'] = max(10.0, 95.0 - (i * 1.2))
    base['image_url'] = images[i % len(images)]
    base['commission_amount'] = 15.0 + (i * 2.5)
    base['region'] = 'BR' if i < 60 else 'US'
    
    if 'score_breakdown' not in base:
        base['score_breakdown'] = {}
    base['score_breakdown']['revenue_estimate'] = 400 + i*10
    new_items.append(base)

payload['entries'] = new_items

new_report = Report(
    id=str(uuid.uuid4()),
    run_id=latest_report.run_id,
    week_start=latest_report.week_start,
    status='published',
    report_payload=payload,
    created_at=datetime.now(timezone.utc)
)

session.add(new_report)
session.commit()
print('Successfully generated 75 products (60 BR, 15 US) into a new Ranking Report!')
