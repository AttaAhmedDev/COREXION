# COREXION

Marketing site for COREXION, served by Django. Pages live as HTML templates in `pages/` and `index.html`. Copy and photos come from PostgreSQL (`PageSection`) and are rendered on the server.

## Requirements

- Python 3.12+
- PostgreSQL

## Local setup

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux

pip install -r requirements.txt
copy .env.example .env          # then set POSTGRES_PASSWORD
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000/

Do not open the HTML files directly in a browser. They contain Django template tags and only work through the server.

## Configuration

Copy `.env.example` to `.env`. Never commit `.env`.

| Variable | Purpose |
|---|---|
| `POSTGRES_*` | Database connection |
| `DJANGO_SECRET_KEY` | Required when `DJANGO_DEBUG=0` |
| `DJANGO_DEBUG` | `1` locally, `0` in production |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated hostnames |
| `THROTTLE_*` | API rate limits |

Admin is at `/staff-portal-fa2026/` (see `ADMIN_PATH` in `config/urls.py`).

## Content

- Edit sections in Django admin. Each row is `page_slug` + `section_key`.
- Replacing or deleting an image removes the file from disk unless another section still uses it.
- Uploads go to `media/sections/` and are gitignored. Back them up with the database.
- Public pages are listed in `config/pages.py`. Add a line there when you add a page.

## API

`GET /api/sections/?page_slug=home` is still available (read-only, rate limited). The website does not use it; pages are rendered on the server.

## Tests

```bash
python manage.py test content
```
