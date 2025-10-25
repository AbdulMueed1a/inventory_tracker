# Inventory Tracker

Small Django REST API to manage inventory items and user signup/authentication.

## Quick overview
- Apps: `stock` (item CRUD) and `user` (signup + JWT).
- API base paths:
  - /api/       -> stock endpoints
  - /api/auth/  -> authentication & user signup endpoints

## Tech stack
- Python 3.8+
- Django
- Django REST Framework
- djangorestframework-simplejwt (JWT auth)
- SQLite by default (configurable to PostgreSQL, etc.)

## Prerequisites
- python 3.8+
- pip
- virtualenv (recommended)

## Environment
Create a `.env` file with at least:
- DJANGO_SECRET_KEY=<your-secret-key>
- DEBUG=True  # or False

Database: Default is SQLite. For PostgreSQL or others, update DATABASES in settings and set related env vars.

## Install & Run

1. Clone the repo:
   - git clone https://github.com/AbdulMueed1a/inventory_tracker.git
   - cd inventory-tracker

2. Create & activate virtualenv:
   - python -m venv .venv
   - macOS / Linux:
     - source .venv/bin/activate
   - Windows (PowerShell / cmd):
     - .venv\Scripts\Activate.ps1  # PowerShell
     - .venv\Scripts\activate.bat  # cmd

3. Install dependencies:
   - python -m pip install --upgrade pip
   - pip install -r requirements.txt

4. Migrate and (optionally) create a superuser:
   - python manage.py migrate
   - python manage.py createsuperuser  # optional

5. Run the development server:
   - python manage.py runserver 0.0.0.0:8000

Local base URL: http://127.0.0.1:8000

Note on versioning: current endpoints use /api/. For public or long-term projects consider using /api/v1/ for versioning.

## Running tests
- python manage.py test

## Endpoints (as implemented)

1) Items (stock)
- List / create
  - GET  /api/items/    -> list items (public)
  - POST /api/items/    -> create item (auth required for writes)
- Detail / update / delete
  - GET    /api/items/<id>/  -> retrieve item
  - PUT    /api/items/<id>/  -> full update (auth required)
  - PATCH  /api/items/<id>/  -> partial update (auth required)
  - DELETE /api/items/<id>/  -> delete (auth required)

Item JSON fields (serializer):
- id: integer
- name: string
- price: decimal (max_digits=10, decimal_places=2)
- added: datetime (auto)
- expiry: date (YYYY-MM-DD)
- quantity: integer
- low_stock: integer
- in_stock: boolean (read-only, computed)
- days_remaining: integer (read-only, computed)
- is_expired: boolean (computed)

Validation highlights:
- price >= 0
- quantity >= 0
- expiry cannot be in the past (where validated)

Permissions:
- Read is public; create/update/delete require authenticated user (IsAuthenticatedOrReadOnly).

2) Authentication & User
- Register (signup):
  - POST /api/auth/users/  -> create user
    - payload: { "username", "email", "password", "password_confirm", "first_name", "last_name" }
  - Response: on successful registration the endpoint returns the created user data plus JWT tokens:
    - `access` (short-lived JWT access token)
    - `refresh` (JWT refresh token)

Example successful response (HTTP 201):
```json
{
  "username": "alice",
  "email": "a@b.com",
  "first_name": "Alice",
  "last_name": "A",
  "access": "<access_token>",
  "refresh": "<refresh_token>"
}
```

- JWT token endpoints (simplejwt):
  - POST /api/auth/token/         -> obtain access & refresh tokens (username & password)
  - POST /api/auth/token/refresh/ -> refresh access token
  - POST /api/auth/token/verify/  -> verify token

Security note: treat tokens as sensitive (don't log or expose them). If you prefer storing the refresh token in an HttpOnly cookie rather than returning it in JSON, that requires server-side changes.

## Examples

Register (signup) — returns tokens on success:
```bash
curl -X POST http://127.0.0.1:8000/api/auth/users/ \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","email":"a@b.com","password":"Secret123!","password_confirm":"Secret123!","first_name":"Alice","last_name":"A"}'
```

Obtain tokens (alternative using token endpoint):
```bash
curl -X POST http://127.0.0.1:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"Secret123!"}'
```

Create item (with JWT access token):
```bash
curl -X POST http://127.0.0.1:8000/api/items/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{"name":"Milk","price":"2.50","expiry":"2025-12-31","quantity":10,"low_stock":2}'
```

List items (public):
```bash
curl http://127.0.0.1:8000/api/items/
```

## Example error responses

Validation error (400):
```json
{
  "price": ["Ensure this value is greater than or equal to 0."]
}
```

Authentication required (401):
```json
{
  "detail": "Authentication credentials were not provided."
}
```

## Notes
- This README documents the current implementation; no source code changes are required to match this behavior.
- The signup endpoint returns JWT tokens for immediate authenticated use after registration.
- If you'd like additional sections (contributing, CI, linting, Docker, or switching to PostgreSQL examples) I can add them.
