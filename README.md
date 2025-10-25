# Inventory Tracker

Small Django REST API to manage inventory items and user signup/authentication.

## Quick overview
- Apps: `stock` (Item CRUD) and `user` (signup + JWT token endpoints).
- API base paths:
  - /api/       -> stock endpoints
  - /api/auth/  -> authentication & user signup endpoints

## Prerequisites
- Python 3.8+
- pip
- virtualenv (recommended)

## Environment
Create a `.env` file with:
- DJANGO_SECRET_KEY=<your-secret-key>
- DEBUG=True (or 0=False)

## Install & Run

1. Clone the repo and enter it:
   - git clone https://github.com/<your-user-or-org>/inventory-tracker.git
   - cd inventory-tracker

2. Create and activate virtualenv:
   - python -m venv .venv
   - macOS / Linux:
     - source .venv/bin/activate
   - Windows (PowerShell):
     - .venv\Scripts\Activate.ps1
   - Windows (cmd):
     - .venv\Scripts\activate.bat

3. Upgrade pip and install requirements:
   - python -m pip install --upgrade pip
   - pip install -r requirements.txt

4. Apply migrations and (optionally) create a superuser:
   - python manage.py migrate
   - python manage.py createsuperuser  # optional

5. Run the development server (choose one):

   - Using Django's dev server:
     - python manage.py runserver 0.0.0.0:8000

   - Using the `uv` package manager :
     - Install and use `uv` according to your local setup.
     - Typical steps (replace with the exact `uv` commands you use):
       - uv install                # install dependencies via uv (if used for dependency management)
       - uv exec -- python -m pip install -r requirements.txt
       - uv exec -- python manage.py runserver 0.0.0.0:8000
     - Note: replace the example `uv` commands above with the exact commands required by your `uv` configuration.

Local base URL: http://127.0.0.1:8000

## Endpoints (as implemented)

1) Items (stock)
- List / create
  - GET  /api/items/    -> list items (public)
  - POST /api/items/    -> create item (authentication required for write)
- Detail / update / delete
  - GET    /api/items/<id>/  -> retrieve item
  - PUT    /api/items/<id>/  -> full update (auth required)
  - PATCH  /api/items/<id>/  -> partial update (auth required)
  - DELETE /api/items/<id>/  -> delete (auth required)

Item JSON fields (as exposed by the serializer):
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

Notes on validation (serializer enforces):
- price >= 0
- quantity >= 0
- expiry cannot be in the past where validated

Permissions:
- Read is public; create/update/delete require authenticated user (IsAuthenticatedOrReadOnly).

2) Authentication & User
- Register (signup):
  - POST /api/auth/users/  -> create user
    - payload: { "username", "email", "password", "password_confirm", "first_name", "last_name" }
  - Response: on successful registration the endpoint returns the created user data plus JWT tokens:
    - `access` (short-lived JWT access token)
    - `refresh` (JWT refresh token)
  - Example successful response (HTTP 201):
    {
      "username": "alice",
      "email": "a@b.com",
      "first_name": "Alice",
      "last_name": "A",
      "access": "<access_token>",
      "refresh": "<refresh_token>"
    }
  - Security note: treat tokens as sensitive (do not log or expose them).

- JWT token endpoints (from simplejwt):
  - POST /api/auth/token/         -> obtain access & refresh tokens (username & password)
  - POST /api/auth/token/refresh/ -> refresh access token
  - POST /api/auth/token/verify/  -> verify token

## Examples

Register (signup) — updated (token returned on success):
curl -X POST http://127.0.0.1:8000/api/auth/users/ \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","email":"a@b.com","password":"Secret123!","password_confirm":"Secret123!","first_name":"Alice","last_name":"A"}'

Example response (HTTP 201):
{
  "username": "alice",
  "email": "a@b.com",
  "first_name": "Alice",
  "last_name": "A",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}

Obtain tokens (alternative using token endpoint):
curl -X POST http://127.0.0.1:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"Secret123!"}'

Create item (with JWT access token):
curl -X POST http://127.0.0.1:8000/api/items/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{"name":"Milk","price":"2.50","expiry":"2025-12-31","quantity":10,"low_stock":2}'

List items (public):
curl http://127.0.0.1:8000/api/items/

## Notes
- The signup endpoint now returns JWT tokens for immediate authenticated use after registration.
- This README documents the current implementation; no code changes other than the signup view behavior (tokens included) are required.
- If you want the refresh token stored as an HttpOnly cookie instead of returned in JSON, mention that and I can outline server-side changes.
