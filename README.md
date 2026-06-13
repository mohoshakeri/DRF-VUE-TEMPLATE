# DRF Vue Template

A starter template for integrated Django REST Framework and Vue 3 TypeScript projects.

This document is the single checklist for project style, structure, and development. Future AI and developer changes must keep the code aligned with it.

## Project Snapshot

- [ ] Backend uses Django, Django REST Framework, and a custom mobile-based user model.
- [ ] Authentication uses verification codes, Redis-backed temporary storage, and token sessions.
- [ ] SMS delivery goes through `services/sms.py`; the current implementation is mock-only and replaceable.
- [ ] Admin is available for users and internal manager models.
- [ ] Generic Python helpers live in `tools/`.
- [ ] Django-aware helpers live in `utils/`.
- [ ] Frontend uses Vue 3, TypeScript, Vite, Vue Router, and Pinia.
- [ ] The client is intentionally minimal and almost unstyled.

## Source Of Truth

- [ ] Read this README before changing code.
- [ ] Keep new conventions in this file, not scattered across separate documents.
- [ ] Update this checklist when a new recurring project style appears.
- [ ] Do not create competing style documents.

## Repository Structure

```text
authentication/  User model, verification code auth, serializers, views, auth services
manager/         Internal admin and cron tracking app
project/         Settings, root URLs, WSGI, logging
services/        Swappable integrations: Redis, SMS, Celery
tools/           Pure Python helpers with no Django dependency
utils/           Django-aware helpers: admin, permissions, validators, tags, views
tests/           All project tests and shared test helpers
client/          Vue 3 TypeScript client
CONSTANTS.py     Shared constants, statuses, cache prefixes, magic values
README.md        Main style, structure, and development checklist
```

## General Style Checklist

- [ ] Keep code practical, typed, explicit, and easy to scan.
- [ ] Do not add module-level docstrings at the top of files.
- [ ] Do not write long comments.
- [ ] Do not write obvious comments.
- [ ] Use short English section separators when a file has multiple logical blocks.
- [ ] Do not leave long code blocks without a separator.
- [ ] Prefer small files and functions over large mixed files.
- [ ] Prefer existing project patterns over new abstractions.
- [ ] Add an abstraction only when it removes real duplication or complexity.
- [ ] Keep unrelated refactors out of task-focused changes.
- [ ] Keep generated or build output out of git unless explicitly required.

Good separator:

```python
# --- Verification Section ---
```

## Python Style Checklist

- [ ] Add type annotations for function parameters.
- [ ] Add return type annotations.
- [ ] Add important variable annotations when the type is not obvious.
- [ ] Use `.format()` for system strings, cache keys, URLs, and predictable strings.
- [ ] Do not use f-strings in Python project code.
- [ ] Use guard clauses and early returns instead of deep `if/else`.
- [ ] Keep business logic out of views.
- [ ] Put business logic in service functions, model methods, or helper modules.
- [ ] Do not import `django.contrib.auth.models.User`.
- [ ] Use the project user model directly inside `authentication`.
- [ ] Use `get_user_model()` outside the auth app when dynamic access is needed.
- [ ] Use `get_object_or_error` from `utils.views`.
- [ ] Do not use Django `get_object_or_404`.
- [ ] Keep imports explicit across app boundaries.
- [ ] Use star imports only inside local app modules with controlled `__all__`.

## Comments And Docstrings Checklist

- [ ] Do not add module docstrings.
- [ ] Do not add long utility method docstrings.
- [ ] View classes may have a short HTTP-method docstring only.
- [ ] Comments must be English.
- [ ] Comments must explain intent, not repeat the code.
- [ ] Use section comments before complex or long logical blocks.

Allowed view docstring:

```python
class CurrentUserView(BaseView):
    """
    GET -> Get Current User
    """
```

## Constants Checklist

- [ ] Put magic numbers in `CONSTANTS.py`.
- [ ] Put cache prefixes in `CONSTANTS.py`.
- [ ] Put shared status choices in `CONSTANTS.py`.
- [ ] Model choice values must be integers.
- [ ] Model choice values must use steps of ten.
- [ ] Do not scatter repeated strings across views, serializers, or services.

## Django Models Checklist

- [ ] Inherit shared model behavior from `utils.db.AbstractModel`.
- [ ] Put state transitions in model methods.
- [ ] Add return annotations to properties.
- [ ] Do not expose sensitive values in `__str__`.
- [ ] Use explicit validators for user input fields.
- [ ] Add migrations for model changes.
- [ ] Confirm migrations with `makemigrations --check --dry-run`.

## Serializer Checklist

- [ ] Always declare `fields`.
- [ ] Never use `exclude`.
- [ ] Do not expose internal fields accidentally.
- [ ] Keep serializer validation focused on input shape and field rules.
- [ ] Keep business decisions outside serializers unless they are validation-specific.
- [ ] Return validation details under `devMessage`.
- [ ] Do not show `devMessage` directly to normal frontend users.

Example:

```python
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields: list[str] = ["id", "mobile", "name", "is_staff"]
```

## API Response Checklist

- [ ] Use named constants from `rest_framework.status`.
- [ ] Do not use raw status integers.
- [ ] `2xx` responses do not need a `message` field.
- [ ] `4xx` responses must include `message`, `devMessage`, or both.
- [ ] Use `message` for user-facing business errors.
- [ ] Use `devMessage` for serializer and developer-only validation details.
- [ ] `5xx` responses must not leak internal details.
- [ ] Keep response keys stable for the frontend.

Error response shape:

```python
return Response(
    {
        "message": "Invalid input.",
        "devMessage": serializer.errors,
    },
    status=status.HTTP_400_BAD_REQUEST,
)
```

## View Checklist

- [ ] Inherit API views from `utils.views.BaseView`.
- [ ] Use guard clauses.
- [ ] Validate input through serializers.
- [ ] Delegate business logic to services.
- [ ] Keep view methods short.
- [ ] Do not query unrelated models in views.
- [ ] Do not handle low-level integration details in views.
- [ ] Assign explicit permission classes.
- [ ] Use throttle scopes where needed.

## Authentication Checklist

Current auth endpoints:

```text
POST /api/v1/auth/request-code/
POST /api/v1/auth/verify-code/
GET  /api/v1/auth/me/
POST /api/v1/auth/logout/
```

- [ ] Verification codes are generated in `authentication/services.py`.
- [ ] Verification codes are stored only in Redis.
- [ ] Verification codes must not have a database model, table, migration, or admin page.
- [ ] Verification codes must be deleted from Redis after successful verification.
- [ ] SMS delivery goes through `services/sms.py`.
- [ ] SMS implementation must be replaceable without changing views.
- [ ] Tokens are created through `utils.session.Session`.
- [ ] Protected endpoints use `Authorization: Bearer <token>`.
- [ ] Invalid or expired tokens must return `401`.
- [ ] Logout must flush the active auth session.

## Service Layer Checklist

- [ ] Put external integrations in `services/`.
- [ ] Keep integrations behind small classes or functions.
- [ ] Keep mock services swappable.
- [ ] Do not import views from services.
- [ ] Log meaningful integration events.
- [ ] Do not log secrets, passwords, or full tokens.

## Utils And Tools Checklist

- [ ] Put pure Python helpers in `tools/`.
- [ ] Put Django-aware helpers in `utils/`.
- [ ] Keep `utils.tags` generic.
- [ ] Do not add project-specific website route helpers to `utils.tags`.
- [ ] Keep validators serializable for migrations.
- [ ] Preserve backward-compatible aliases when fixing misspelled public validators.

Useful template tags and filters:

```text
standard_datetime, standard_date, en_datetime
to_iso_number, to_string, persian_digits, english_digits
disk, site_disk, query_update
multiply, divide, percent
```

## Admin Checklist

- [ ] Register important models in admin.
- [ ] Use `utils.admin.AbstractAdmin`.
- [ ] Exclude sensitive fields from list displays.
- [ ] Keep readonly audit fields readonly.
- [ ] Add useful search fields.
- [ ] Add useful filters.
- [ ] Keep admin actions explicit and safe.

## Backend Run Checklist

- [ ] Install Python dependencies.
- [ ] Configure `.env` or development settings.
- [ ] Ensure PostgreSQL and Redis are available for development settings.
- [ ] Use test settings when local PostgreSQL is not available.
- [ ] Run migrations before running the server.

Common commands:

```bash
.venv/bin/python manage.py check
.venv/bin/python manage.py migrate
.venv/bin/python manage.py runserver 0.0.0.0:4110
```

Database-independent checks:

```bash
env DJANGO_SETTINGS_MODULE=project.settings.test .venv/bin/python manage.py test
env DJANGO_SETTINGS_MODULE=project.settings.test .venv/bin/python manage.py makemigrations --check --dry-run
```

## Frontend Structure Checklist

```text
client/src/
  api/
    client.ts
    call.ts
    errors.ts
    services/
  components/
  constants/
  layouts/
  plugins/
  pwa/
  router/
  stores/
  styles/
  utils/
  validators/
  views/
```

- [ ] Use Vue 3.
- [ ] Use TypeScript.
- [ ] Use Vite.
- [ ] Use Pinia for shared state.
- [ ] Use Vue Router for navigation.
- [ ] Keep the base client almost unstyled.
- [ ] Keep repeated strings in constants.
- [ ] Keep global CSS in `styles/`.

## Vue Component Checklist

- [ ] Use `<script setup lang="ts">`.
- [ ] Use absolute imports from `/src`.
- [ ] Keep components small and reusable.
- [ ] Keep page-local state inside views.
- [ ] Every page must use a layout.
- [ ] Views may call API services.
- [ ] Views must not call `axios` directly.
- [ ] Views must not contain backend error mapping.
- [ ] Views must not control global loading manually when an API request exists.
- [ ] Use computed values for derived display state.
- [ ] Keep templates readable.
- [ ] Avoid complex inline template expressions.

## Frontend API Checklist

- [ ] All backend calls go through `apiCall`.
- [ ] API service files own raw endpoint paths.
- [ ] Views import API service functions.
- [ ] API client handles the base URL.
- [ ] API client attaches authorization headers.
- [ ] API layer handles JSON responses.
- [ ] API layer handles HTML responses.
- [ ] API layer handles `FormData`.
- [ ] API layer handles timeouts.
- [ ] API layer handles network errors.
- [ ] API layer handles `401` cleanup and redirect.
- [ ] API layer controls global loading.
- [ ] API layer sends global messages.
- [ ] Failed handled requests return `undefined`.

Allowed API return values:

```text
Object
Array
String
Blob
undefined
```

## Frontend Storage Checklist

- [ ] Direct `localStorage` access is allowed only in `client/src/utils/storage.ts`.
- [ ] Auth token storage uses `AUTH_TOKEN_KEY`.
- [ ] Dark mode storage uses `DARK_MODE_KEY`.
- [ ] Router guards must not trust storage alone.
- [ ] Invalid tokens must be removed.

## Frontend Router Checklist

- [ ] Routes live in `client/src/router/routes.ts`.
- [ ] Guards live in `client/src/router/guards.ts`.
- [ ] Router setup lives in `client/src/router/index.ts`.
- [ ] Every route must have an explicit name.
- [ ] Protected routes use `meta: {requiresAuth: true}`.
- [ ] Public routes use `meta: {requiresAuth: false}`.
- [ ] Guest-only auth pages use `meta: {guestOnly: true}`.
- [ ] Guards handle guest redirects.
- [ ] Guards handle authenticated redirects.
- [ ] Guards load current user data when needed.
- [ ] Guards clean invalid tokens.

## Frontend Message Checklist

- [ ] Use `sendMessage`.
- [ ] Do not use `alert`.
- [ ] Do not show backend `devMessage` to normal users.
- [ ] Normalize backend error messages in `api/errors.ts`.

Allowed statuses:

```text
primary
success
warning
danger
info
```

## Frontend Validation Checklist

- [ ] Validate forms before API calls.
- [ ] Use object-based validation rules.
- [ ] Keep reusable regex rules in `validators/regex.ts`.
- [ ] Normalize Persian and Arabic digits on numeric inputs.
- [ ] Use `v-normalize-digits` only for numeric inputs.
- [ ] Do not mutate business values just for display formatting.

Example:

```ts
const isValid = await verifyForm([
  {
    val: mobile.value,
    reg: MOBILE_REGEX,
    msg: "Invalid mobile number.",
  },
]);
```

## CSS Checklist

- [ ] Keep base client styling minimal.
- [ ] Global CSS belongs in `styles/app.css`.
- [ ] CSS variables belong in `styles/variables.css`.
- [ ] Reusable helpers belong in `styles/helpers.css`.
- [ ] Component styles must be scoped unless intentionally global.
- [ ] Use CSS variables for theme values.
- [ ] Do not add a design system unless the task asks for it.
- [ ] Avoid decorative styling in this template client.

## Frontend Run Checklist

- [ ] Install client dependencies before typecheck or build.
- [ ] Configure `VITE_BACKEND_BASE_URL` when needed.
- [ ] Run typecheck after TypeScript changes.
- [ ] Run build after frontend structure changes.

Commands:

```bash
cd client
npm install
npm run dev
npm run typecheck
npm run build
```

Default backend base URL:

```text
VITE_BACKEND_BASE_URL=http://localhost:4110/api/v1
```

## Testing And Verification Checklist

- [ ] Put all tests in the top-level `tests/` directory.
- [ ] Do not put test cases inside Django app folders.
- [ ] Name test files as `tests/test_<feature>.py`.
- [ ] Keep shared test utilities in `tests/api_helpers.py` or focused helper modules under `tests/`.
- [ ] Run Python syntax checks for touched Python files.
- [ ] Run Django system check.
- [ ] Run Django tests with normal settings when the local database is available.
- [ ] Run Django tests with test settings when PostgreSQL is unavailable.
- [ ] Run migration dry-run checks.
- [ ] Run frontend typecheck after TypeScript changes.
- [ ] Run frontend build after frontend changes.
- [ ] Run `git diff --check` before finishing.
- [ ] Report any skipped checks and why.

Recommended final commands:

```bash
find . -path './.venv' -prune -o -path './client/node_modules' -prune -o -name '*.py' -print -exec python3 -m py_compile {} +
.venv/bin/python manage.py check
env DJANGO_SETTINGS_MODULE=project.settings.test .venv/bin/python manage.py test
env DJANGO_SETTINGS_MODULE=project.settings.test .venv/bin/python manage.py makemigrations --check --dry-run
git diff --check
```

Frontend final commands:

```bash
cd client
npm run typecheck
npm run build
```

## AI Development Checklist

- [ ] Read this README first.
- [ ] Use `rg` to find relevant files.
- [ ] Inspect existing patterns before editing.
- [ ] Make the smallest coherent change.
- [ ] Do not revert user changes.
- [ ] Do not introduce unrelated refactors.
- [ ] Keep backend and frontend contracts aligned.
- [ ] Add constants for repeated values.
- [ ] Add serializers for new API inputs and outputs.
- [ ] Add services for new business workflows.
- [ ] Add URL routes for new views.
- [ ] Add admin registrations for operational models.
- [ ] Add or update migrations for model changes.
- [ ] Add focused tests when behavior risk is meaningful.
- [ ] Update this checklist when new project style becomes standard.

## Anti-Pattern Checklist

- [ ] No module-level docstrings.
- [ ] No long comments.
- [ ] No f-strings in Python project code.
- [ ] No raw status integers.
- [ ] No serializer `exclude`.
- [ ] No raw `axios` in views.
- [ ] No direct `localStorage` outside storage utilities.
- [ ] No business logic in views.
- [ ] No project-specific route helpers in `utils.tags`.
- [ ] No secrets in frontend env files.
- [ ] No internal errors shown to users.
- [ ] No unverified assumptions about auth state.
