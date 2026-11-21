#!/usr/bin/env python3
"""gen_golden_data — deterministic synthetic test data for the golden platforms (seed S15).

Writes JSON Lines under generated/golden-data/ (not committed): tenants, listings (10,000), buyers, orders,
and simulator scripts for payments, carriers and messaging. All values are synthetic: no real people; phone
numbers are synthetic and must never be dialled (all
messages go to the messaging simulator, CTX-L4), and emails use the reserved example.com domain (RFC 2606).

The digest of the output is recorded in spec/seed/golden-data.sha256; CI regenerates the data and fails if the
digest changes without the recorded value being updated, so tests always run on identical data.

Usage: python3 tools/gen_golden_data.py [outdir] [--check]
"""
import hashlib, json, os, random, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CROCKFORD = '0123456789ABCDEFGHJKMNPQRSTVWXYZ'
EPOCH_MS = 1798761600000            # 2027-01-01T00:00:00Z: fixed so ids are stable

def ugid(kind, n):
    """Deterministic ULID-shaped id: 10 chars of time + 16 chars of counter."""
    t, out = EPOCH_MS + n, ''
    for _ in range(10):
        out = CROCKFORD[t % 32] + out; t //= 32
    c, tail = n, ''
    for _ in range(16):
        tail = CROCKFORD[c % 32] + tail; c //= 32
    return f'ucos:{kind}:{out}{tail}'

def money(amount, cur):
    return {'amount': f'{amount:.2f}', 'currency': cur}

def generate(rnd):
    tenants = [
        {'id': ugid('tenant', 1), 'slug': 'bazaar', 'platform': 'd2c-in-ae', 'countries': ['IN', 'AE']},
        {'id': ugid('tenant', 2), 'slug': 'metro-distrib', 'platform': 'b2b-in', 'countries': ['IN']},
        {'id': ugid('tenant', 3), 'slug': 'kala', 'platform': 'd2c-in-ae', 'countries': ['IN']},
        {'id': ugid('tenant', 4), 'slug': 'souq-hub', 'platform': 'marketplace-in-ae', 'countries': ['IN', 'AE']},
        {'id': ugid('tenant', 5), 'slug': 'sample', 'platform': 'sample-p0', 'countries': ['IN']},
    ]
    cats = [('apparel-and-accessories', 'apparel-low', 199, 2499), ('home-kitchen', 'household-standard', 99, 4999),
            ('grocery-gourmet-food', 'food-5', 49, 1999), ('electronics', 'household-standard', 499, 79999)]
    listings = []
    for i in range(10000):
        t = tenants[i % 4]
        cat, taxcat, lo, hi = cats[i % len(cats)]
        inr = round(rnd.uniform(lo, hi), 0)
        listings.append({'id': ugid('listing', i + 1), 'tenant': t['id'], 'sku': f'SKU-{i + 1:05d}', 'category': cat,
                         'taxCategory': taxcat, 'price': {'IN': money(inr, 'INR'), 'AE': money(round(inr / 22.7, 0), 'AED')},
                         'stock': rnd.randint(0, 200), 'status': 'published' if i % 50 else 'draft'})
    buyers = []
    for i in range(2000):
        cc = 'IN' if i % 4 else 'AE'
        buyers.append({'id': ugid('party', i + 1), 'name': f'Test Buyer {i + 1}', 'email': f'buyer{i + 1}@example.com',
                       'phone': f'+91 70000 {i:05d}' if cc == 'IN' else f'+971 50 000 {i:04d}',
                       'country': cc, 'consents': {'marketing-whatsapp': i % 3 == 0}})
    orders = []
    for i in range(5000):
        b = buyers[i % len(buyers)]
        lines = [listings[rnd.randrange(len(listings))] for _ in range(rnd.randint(1, 3))]
        cur = 'INR' if b['country'] == 'IN' else 'AED'
        total = sum(float(l['price'][b['country']]['amount']) for l in lines)
        method = rnd.choice(['upi', 'card', 'cod'] if cur == 'INR' else ['card', 'cod'])
        orders.append({'id': ugid('order', i + 1), 'buyer': b['id'], 'lines': [l['id'] for l in lines],
                       'total': money(total, cur), 'paymentMethod': method,
                       'outcome': rnd.choices(['delivered', 'returned', 'cancelled', 'rto'], [80, 8, 8, 4])[0]})
    simulators = {
        'payment': [{'case': 'capture', 'reply': 'captured'}, {'case': 'decline', 'reply': 'failed', 'reason': 'insufficient-funds'},
                    {'case': 'timeout', 'reply': 'pending', 'afterSeconds': 30}],
        'carrier': [{'case': 'happy', 'timeline': ['created', 'picked-up', 'in-transit', 'out-for-delivery', 'delivered']},
                    {'case': 'ndr', 'timeline': ['created', 'picked-up', 'out-for-delivery', 'exception']},
                    {'case': 'rto', 'timeline': ['created', 'picked-up', 'exception', 'rto-initiated', 'rto-delivered']}],
        'messaging': [{'case': 'delivered', 'reply': 'delivered'}, {'case': 'bounce', 'reply': 'bounced'}],
    }
    return {'tenants': tenants, 'listings': listings, 'buyers': buyers, 'orders': orders, 'simulators': [simulators]}

def write(outdir):
    data = generate(random.Random(20270101))
    os.makedirs(outdir, exist_ok=True)
    h = hashlib.sha256()
    for name in sorted(data):
        body = ''.join(json.dumps(r, sort_keys=True, ensure_ascii=False) + '\n' for r in data[name])
        open(os.path.join(outdir, f'{name}.jsonl'), 'w', encoding='utf-8').write(body)
        h.update(name.encode()); h.update(body.encode())
    return h.hexdigest(), {k: len(v) for k, v in data.items()}

def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    outdir = args[0] if args else os.path.join(ROOT, 'generated', 'golden-data')
    digest, sizes = write(outdir)
    rec = os.path.join(ROOT, 'spec', 'seed', 'golden-data.sha256')
    if '--check' in sys.argv:
        want = open(rec).read().split()[0] if os.path.exists(rec) else None
        if digest != want:
            print(f'golden data digest {digest} != recorded {want} (regenerate and update spec/seed/golden-data.sha256 deliberately)')
            sys.exit(1)
        print(f'golden data reproducible: {digest[:16]}… {sizes}')
        return
    open(rec, 'w').write(f'{digest}  generated/golden-data (tools/gen_golden_data.py)\n')
    print(f'wrote {sizes} to {outdir}; digest {digest[:16]}…')

if __name__ == '__main__':
    main()
