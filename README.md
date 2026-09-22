# BAM Studio — Website & CMS

Production-ready Flask + Jinja2 CMS-driven website for BAM Studio.  
Design language aligned with [Jhapa City FC](https://jhapacityfc.vercel.app) (Orbitron + Inter, dark navy, neon gold accents).

## Stack

- **Frontend:** HTML5, CSS3, Vanilla JS, Jinja2
- **Backend:** Python, Flask
- **Database:** PostgreSQL (Neon) or SQLite for local
- **Media:** Cloudinary
- **Deploy:** Vercel / any WSGI host

## Quick start

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with SECRET_KEY, DATABASE_URL, Cloudinary keys
python seed.py
python app.py
```

- Public site: http://127.0.0.1:5000  
- Admin: http://127.0.0.1:5000/admin/login  
- Default admin: `admin@argonbhujel` / `Argon_017` (change immediately)

## Environment

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | Neon/Postgres connection string (or omit for SQLite) |
| `SECRET_KEY` | Flask secret |
| `CLOUDINARY_*` | Cloud name, API key, secret |
| `ADMIN_EMAIL` / `ADMIN_PASSWORD` | Used by seed |

## Admin capabilities

- Theme editor (colors, fonts, spacing, animations) → CSS variables
- Projects (CRUD, publish, feature, gallery URLs)
- Services, Pricing, Team, Partnerships
- Navigation, General settings, Leads
- Media upload via Cloudinary
- Contact form → Leads pipeline

## Design DNA (from Jhapa FC)

- Display: **Orbitron** (heavy weight, wide letter-spacing)
- Body: **Inter**
- Background: `#0c1929`
- Primary / neon: `#f5c542`
- Secondary: `#38bdf8`
- Glass cards, rounded 16–24px, cyan/gold borders
- Scroll reveal via IntersectionObserver

## Notes

- Do not invent testimonials or stats — sections hide when empty.
- Partnership badge is editable and can be removed from admin.
- For production: use Neon PostgreSQL, strong SECRET_KEY, HTTPS, and change default admin password.

## License

Private — BAM Studio.


## Deploy on Vercel

1. Push repo to GitHub
2. Import project on [vercel.com](https://vercel.com)
3. Framework: Other / Python
4. Environment variables:
   - `SECRET_KEY`
   - `DATABASE_URL` (Neon PostgreSQL recommended)
   - `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET` (optional)
   - `ADMIN_EMAIL`, `ADMIN_PASSWORD` (for first seed)
5. After first deploy, run seed once via SSH/one-off or local against production DB:
   `DATABASE_URL=... python seed.py`

SQLite on Vercel is ephemeral — use **Neon** Postgres for production.
