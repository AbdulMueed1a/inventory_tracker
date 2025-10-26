# Backend Changes (detailed log)

This document records all modifications applied to the backend codebase during the recent debugging and frontend-integration work. Each section lists the file(s) changed, what was changed, why the change was required, and any follow-up or recommended actions.

---

## 1) Inventory_tracker/settings.py
Files changed
- E:\flutter_projects\Backend\inventory_tracker\Inventory_tracker\settings.py

What was changed
- Added a runtime check to detect whether `django-cors-headers` is installed:
  - importlib.util.find_spec("corsheaders") used to set `CORS_AVAILABLE`.
- Conditionally append `'corsheaders'` to `INSTALLED_APPS` only when the package is present.
- Conditionally insert `'corsheaders.middleware.CorsMiddleware'` into `MIDDLEWARE` (at index 0) when available.
- Added CORS configuration variables:
  - `CORS_ALLOW_ALL_ORIGINS = True` and `CORS_ALLOW_CREDENTIALS = True` when corsheaders present; otherwise defined as False to avoid undefined variable errors.
- Updated `REST_FRAMEWORK` settings:
  - Added `'rest_framework_simplejwt.authentication.JWTAuthentication'` to `DEFAULT_AUTHENTICATION_CLASSES` (kept `SessionAuthentication` also present).
  - Added `'rest_framework.permissions.IsAuthenticatedOrReadOnly'` as `DEFAULT_PERMISSION_CLASSES`.

Why this change was necessary
- Cross-Origin Resource Sharing (CORS): Frontend clients (web or emulator) were failing to fetch backend endpoints due to CORS/preflight problems. Adding `corsheaders` and enabling global CORS during development allows browser-based or cross-origin clients to make requests to the API.
- Defensive packaging: Some development environments may not have `django-cors-headers` installed yet. The conditional detection prevents Django from failing to start with ModuleNotFoundError; it allows the developer to install the package and enable CORS without crashing the app in the meantime.
- JWT acceptance: The project uses djangorestframework-simplejwt for token issuance, but DRF needed to be configured to accept JWT `Authorization: Bearer <token>` headers. Adding `JWTAuthentication` ensures the DRF views accept and parse Bearer tokens, preventing 403/401 responses when valid tokens are supplied.
- Permission defaults: Setting `IsAuthenticatedOrReadOnly` makes reads public while requiring authentication for writes — this simplifies endpoint protection and matched frontend expectations.

Follow-up / recommendations
- Install the package: `pip install django-cors-headers`.
- For production, replace `CORS_ALLOW_ALL_ORIGINS = True` with a restricted `CORS_ALLOWED_ORIGINS` whitelist and tighten `CORS_ALLOW_CREDENTIALS` as needed.
- Consider removing the conditional app/middleware once `corsheaders` becomes a required dependency for the project.

---

## 2) user/views.py
Files changed
- E:\flutter_projects\Backend\inventory_tracker\user\views.py

What was changed
- Signup view now returns JWT tokens as part of the signup response:
  - After creating the user, a refresh token is created via `RefreshToken.for_user(user)`.
  - Response JSON now contains `access` and `refresh` tokens alongside the serialized user data.
- Added CORS response headers to the signup POST response for a quick fix:
  - `Access-Control-Allow-Origin: *`
  - `Access-Control-Allow-Methods: POST, OPTIONS`
  - `Access-Control-Allow-Headers: Content-Type, Authorization`
- Implemented an `options` handler on the SignupView to respond to preflight (OPTIONS) requests with appropriate CORS headers.

Why this change was necessary
- Token on signup: The frontend workflow expects to receive an access and refresh token immediately upon user registration so the app can persist them and consider the user authenticated. Returning tokens from signup avoids a second login step and simplifies onboarding flows.
- CORS / preflight: When the browser or certain clients POST to `/api/auth/users/`, the browser may perform an OPTIONS preflight. If the server doesn't respond with proper CORS headers (or handle OPTIONS requests), the browser blocks the request. Adding these headers and an explicit `options` method ensures the signup endpoint works from cross-origin frontends while the global CORS setup is being completed.

Notes and caveats
- These per-view CORS headers are a pragmatic, short-term fix. The recommended long-term and holistic solution is to install and configure `django-cors-headers` globally (see settings changes above) and remove per-view headers to avoid duplicated logic.
- Returning tokens in JSON is convenient but may not be ideal for all security models. For higher security, consider returning only an access token and placing the refresh token in a secure, HttpOnly cookie with proper CSRF protections.

---

## 3) user/serializers.py
Files changed
- E:\flutter_projects\Backend\inventory_tracker\user\serializers.py

What was changed
- Implemented a `UserSignupSerializer` that:
  - Accepts `username`, `email`, `password`, `password_confirm`, `first_name`, `last_name`.
  - Validates `password_confirm` presence and equality with `password`.
  - Uses Django's `validate_password` for password strength; converts validation errors into serializer `ValidationError`.
  - Checks uniqueness of email and username and raises serializer errors if they already exist.
  - Implements `create()` to set the user's password correctly via `set_password()` and save the user.

Why this change was necessary
- Robust signup experience: Frontend signup needs clear, structured validation errors and a correctly created user record with hashed password. This serializer ensures all checks are centralized server-side.
- Prevents weak or mismatched passwords and duplicate accounts.

Follow-up / recommendations
- If you want to enforce email normalization or case-insensitive uniqueness, add appropriate logic.
- Consider returning explicit field-level errors for front-end display (already done using serializer ValidationError maps).

---

## 4) stock/serializers.py
Files changed
- E:\flutter_projects\Backend\inventory_tracker\stock\serializers.py

What was changed
- Implemented `ItemSerializer` computed/read-only fields:
  - `in_stock` (SerializerMethodField): returns a boolean based on `quantity`.
  - `days_remaining` (SerializerMethodField): returns days until expiry (non-negative int) or `None` when expiry not set.
  - `is_expired` (SerializerMethodField): boolean indicating expired state.
- Implemented `get_days_remaining`, `get_is_expired`, `get_in_stock` methods to avoid AttributeError: missing method implementations caused the earlier exception.
- Added field validators:
  - `validate_quantity` ensures non-negative quantity.
  - `validate_price` ensures non-negative price.
  - `validate_expiry_date` ensures expiry isn't in the past (server timezone-aware comparison).
- Implemented `validate()` to assert that you cannot stock an already-expired item (based on provided `expiry` and `quantity`).

Why this change was necessary
- Fix AttributeError: Previously the serializer declared `days_remaining` but did not define `get_days_remaining`, which raised `AttributeError`. Implementing the getter methods resolves this runtime error.
- Derived fields: The frontend expects `in_stock`, `days_remaining`, and `is_expired` in the item representation to display UI states (red warnings, expiry badges, etc.). Putting this logic in serializers centralizes calculation and keeps the API consistent.
- Validation: Enforces business rules and prevents invalid persisted state (negative prices/quantities or storing already-expired stock).

Notes and caveats
- Ensure the serializer `Meta.model` points to the actual `Item` model (the code in the repository already imports `Item`).
- The serializer uses Django's `timezone` utilities when comparing dates; ensure server timezone is correctly configured.

---

## 5) urls / routing (no functional change but recorded)
Files changed / examined
- E:\flutter_projects\Backend\inventory_tracker\Inventory_tracker\urls.py
- E:\flutter_projects\Backend\inventory_tracker\user\urls.py

What was confirmed
- `user.urls` is mounted under `/api/auth/` and exposes:
  - `token/` (TokenObtainPairView)
  - `token/refresh/`
  - `token/verify/`
  - `users/` (SignupView) — POST creates user and returns tokens
- `stock.urls` is mounted under `/api/` for item CRUD.

Why this is relevant
- The frontend builds URLs against `/api/auth/` and `/api/` — ensure frontend base URL and emulator/device host mapping are correct (see frontend notes below).

---

## Cross-cutting notes (why these backend changes together)
1. Frontend cannot fetch or cannot authenticate:
   - Symptoms: "client failed to fetch URI", 403 responses for write endpoints, AttributeError on item serializer.
   - Causes addressed:
     - CORS / preflight blocking: fixed by enabling corsheaders (or per-view CORS headers as stopgap) and by adding OPTIONS handling for signup.
     - Bearer token rejection: DRF was only configured with `SessionAuthentication`, which expects session cookies and CSRF; adding `JWTAuthentication` allows DRF to accept `Authorization: Bearer <token>` which the frontend sends.
     - Missing serializer methods: implemented getters for computed fields to prevent server 500/AttributeError.
     - Signup flow: returning tokens on signup allows frontend to persist tokens immediately and authenticate subsequent requests.

2. Defensive and incremental approach:
   - Per-view CORS headers were added as an interim quick fix while adding `django-cors-headers` as the proper global solution.
   - Settings are defensive so the server won't crash if `django-cors-headers` is not yet installed (useful during iterative development).

---

## Recommended next steps (actionable)
1. Install `django-cors-headers` in the backend environment:
   - `pip install django-cors-headers`
   - Restart Django server.
   - Remove per-view manual CORS headers from `user.views.SignupView` once global CORS works.
2. Verify frontend behavior:
   - Confirm the frontend uses the correct host IP depending on platform (e.g., Android emulator -> `10.0.2.2`, web -> `127.0.0.1`, physical device -> machine LAN IP).
   - Confirm frontend persists both `access` and `refresh` tokens securely and sends `Authorization: Bearer <access>` for authenticated endpoints.
3. Token lifecycle:
   - Ensure frontend handles 401 by attempting refresh with `refresh` token at `/api/auth/token/refresh/`.
   - Ensure clock skew between client and server is minimal (JWT expiry depends on accurate clocks).
4. Security hardening for production:
   - Replace `CORS_ALLOW_ALL_ORIGINS = True` with `CORS_ALLOWED_ORIGINS` whitelist.
   - Consider storing refresh tokens in secure, HttpOnly cookies with CSRF protections instead of exposing them to JS if appropriate for your app threat model.
   - Audit any endpoints that return tokens in response payloads; consider more secure alternatives if required.

---

## Change log summary (concise)
- settings.py: conditional corsheaders integration; added JWT auth to DRF; default permission class set.
- user/views.py: signup now issues and returns JWT tokens; added CORS response headers; added OPTIONS handler.
- user/serializers.py: robust signup serializer with validation and secure password handling.
- stock/serializers.py: implemented computed fields and validations; fixed AttributeError by adding missing serializer methods.
- README and routing remained consistent with these changes; no route renames were done.

If you want, I can:
- Remove per-view CORS headers from `user.views` after you install `django-cors-headers`.
- Produce a short "how-to" for the frontend to persist and refresh tokens and example cURL/JS/Flutter snippets to verify the end-to-end flow.

