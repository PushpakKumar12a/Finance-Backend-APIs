# Finance Data Processing & Access Control Backend

A Django REST Framework backend for a finance dashboard system with role-based access control, financial record management, and summary analytics.

---

## Table of Contents

- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Setup & Installation](#setup--installation)
- [API Reference](#api-reference)
- [Access Control Matrix](#access-control-matrix)
- [Design Decisions & Assumptions](#design-decisions--assumptions)
- [Testing](#testing)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.13 |
| Framework | Django 6.0 + Django REST Framework 3.17 |
| Database | MySQL |
| Authentication | JWT via `djangorestframework-simplejwt` |
| Filtering | `django-filter` |
| Testing | Django's built-in test framework (`APITestCase`) |

---

## Architecture

```
root
├── .env.example
├── .gitignore
├── manage.py
├── README.md
├── requirements.txt
├── finance_backend/
│   ├── __init__.py
│   ├── asgi.py
│   ├── exceptions.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── management/
│   │   └── commands/
│   │       ├── seed_admin.py
│   │       └── seed_dummy_data.py
│   ├── migrations/
│   ├── models.py
│   ├── permissions.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── records/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── filters.py
│   ├── migrations/
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
└── dashboard/
    ├── __init__.py
    ├── apps.py
    ├── migrations/
    ├── serializers.py
    ├── tests.py
    ├── urls.py
    └── views.py
```

**Separation of concerns:**

- `accounts` — users, authentication, and permission classes
- `records` — financial data and CRUD logic
- `dashboard` — read-only aggregation views
- Permission classes are defined in `accounts` and imported into other apps

---

## Setup & Installation

### Prerequisites

- Python 3.13+
- pip
- MySQL

### Quick Start

```bash
# 1. Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
# .venv\Scripts\activate         # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create a root .env file from the example and edit the values
copy .env.example .env

# 4. Run migrations
python manage.py migrate

# 5. Seed an admin user
python manage.py seed_admin
# Creates: admin@finance.local / admin123456

# 6. Start the server
python manage.py runserver
```

> The MySQL database is created automatically if it does not exist.

---

### Creating Users

The project supports three roles: `viewer`, `analyst`, and `admin`.

#### Admin user

```bash
python manage.py seed_admin

# Override defaults
python manage.py seed_admin --email admin@example.com --username admin --password StrongPass123
```

#### Analyst user

Register a normal account first, then promote it via the admin-only endpoint:

```http
PATCH /api/users/{id}/
Content-Type: application/json

{ "role": "analyst" }
```

You can also update roles directly in Django Admin.

#### Dummy data

```bash
python manage.py seed_dummy_data
```

Creates demo accounts for all three roles and a sample set of income and expense records.

---

### Environment Variables

| Variable | Default | Description |
|---|---|---|
| `DB_NAME` | `finance_db` | MySQL database name |
| `DB_USER` | `root` | MySQL user |
| `DB_PASSWORD` | _(empty)_ | MySQL password |
| `DB_HOST` | `127.0.0.1` | MySQL host |
| `DB_PORT` | `3306` | MySQL port |
| `SECRET_KEY` | _(built-in dev key)_ | Django secret key |

Generate a new secret key:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## API Reference

All protected endpoints require:

```
Authorization: Bearer <access_token>
```

---

### Authentication

#### Register

```
POST /api/auth/register/
```

**Access:** Public — new users are assigned the `viewer` role by default.

```json
{
    "email": "user@example.com",
    "username": "johndoe",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!"
}
```

---

#### Login

```
POST /api/auth/login/
```

**Access:** Public

```json
{
    "email": "user@example.com",
    "password": "SecurePass123!"
}
```

**Response:**

```json
{
    "access": "<jwt_access_token>",
    "refresh": "<jwt_refresh_token>"
}
```

---

#### Refresh Access Token

```
POST /api/auth/refresh/
```

```json
{ "refresh": "<jwt_refresh_token>" }
```

---

#### Get Current User Profile

```
GET /api/auth/me/
```

**Access:** Any authenticated user

---

### User Management

> All endpoints below are restricted to **Admin** only.

#### List All Users

```
GET /api/users/
```

**Query params:** `?search=<email_or_username>`

---

#### Get / Update / Deactivate a User

```
GET    /api/users/{id}/
PATCH  /api/users/{id}/
DELETE /api/users/{id}/
```

**PATCH body:**

```json
{ "role": "analyst", "is_active": true }
```

**DELETE** performs a soft-deactivation. Admins cannot deactivate their own account.

---

### Financial Records

#### List Records

```
GET /api/records/
```

**Access:** Viewer, Analyst, Admin

| Parameter | Description | Example |
|---|---|---|
| `type` | Filter by income/expense | `?type=income` |
| `category` | Case-insensitive match | `?category=salary` |
| `date_from` | On or after date | `?date_from=2026-01-01` |
| `date_to` | On or before date | `?date_to=2026-12-31` |
| `amount_min` | Minimum amount | `?amount_min=100` |
| `amount_max` | Maximum amount | `?amount_max=5000` |
| `search` | Full-text (description, category) | `?search=rent` |
| `ordering` | Sort field (prefix `-` for desc) | `?ordering=-amount` |
| `page` | Page number | `?page=2` |

---

#### Create a Record

```
POST /api/records/
```

**Access:** Admin only

```json
{
    "amount": "1500.00",
    "type": "income",
    "category": "salary",
    "date": "2026-03-15",
    "description": "March salary"
}
```

---

#### Get a Record

```
GET /api/records/{id}/
```

**Access:** Viewer, Analyst, Admin

---

#### Update a Record

```
PATCH /api/records/{id}/
```

**Access:** Admin only — accepts any subset of record fields.

---

#### Delete a Record

```
DELETE /api/records/{id}/
```

**Access:** Admin only — soft-deletes the record (`is_deleted=True`). Not removed from the database.

---

### Dashboard Analytics

All endpoints accept optional `?date_from=YYYY-MM-DD&date_to=YYYY-MM-DD` query params.

**Access:** Analyst, Admin

---

#### Financial Summary

```
GET /api/dashboard/summary/
```

```json
{
    "total_income": "8000.00",
    "total_expenses": "1400.00",
    "net_balance": "6600.00",
    "total_records": 4
}
```

---

#### Category Breakdown

```
GET /api/dashboard/category-breakdown/
```

```json
[
    { "category": "salary",    "type": "income",  "total": "5000.00", "count": 1 },
    { "category": "rent",      "type": "expense", "total": "1200.00", "count": 1 },
    { "category": "groceries", "type": "expense", "total": "200.00",  "count": 1 }
]
```

---

#### Monthly Trends

```
GET /api/dashboard/trends/
```

```json
[
    { "month": "2026-01", "type": "income",  "total": "5000.00", "count": 1 },
    { "month": "2026-01", "type": "expense", "total": "1200.00", "count": 1 },
    { "month": "2026-02", "type": "income",  "total": "3000.00", "count": 1 }
]
```

---

#### Recent Activity

```
GET /api/dashboard/recent-activity/
```

Returns the 10 most recent financial records.

---

## Access Control Matrix

| Action | Viewer | Analyst | Admin |
|---|:---:|:---:|:---:|
| Register / Login | ✅ | ✅ | ✅ |
| View own profile | ✅ | ✅ | ✅ |
| List / View records | ✅ | ✅ | ✅ |
| Create / Update / Delete records | ❌ | ❌ | ✅ |
| Dashboard analytics | ❌ | ✅ | ✅ |
| Manage users | ❌ | ❌ | ✅ |

**Implementation:** Role-based permission classes (`IsAdmin`, `IsAnalystOrAbove`, `IsViewerOrAbove`) are composed in DRF views. Each class checks `request.user.role` against the role hierarchy.

---

## Design Decisions & Assumptions

### Role model

Three fixed roles (`viewer`, `analyst`, `admin`) stored as a `CharField` on the User model. A separate Role table with many-to-many relationships adds complexity that isn't needed for a fixed hierarchy. Migrating to `django-guardian` or a policy-based model would be straightforward if dynamic permissions are needed in the future.

### Authentication

JWT (stateless) — no session cookies, making it suitable for SPA and mobile frontends. Access tokens expire after **1 hour**; refresh tokens last **7 days**. Registration is public but defaults to the `viewer` role. Only admins can promote users.

### Financial records

Records are never truly removed. The `is_deleted` flag combined with a custom `ActiveRecordManager` ensures soft-deleted records are excluded from default queries while remaining auditable.

All authenticated users see all records — this is a shared finance dashboard, not a per-user ledger.

Category is a free-text field rather than an enum, allowing flexible categorization without schema changes.

### Dashboard analytics

All aggregation is done in the database using Django ORM's `aggregate()` and `annotate()` — no Python-side computation. Date range filtering is optional on all dashboard endpoints.

### Error handling

A custom exception handler wraps all DRF errors in a consistent envelope:

```json
{ "error": true, "message": "...", "details": {} }
```

HTTP status codes: `400` validation · `401` unauthenticated · `403` forbidden · `404` not found.

### Pagination

`PageNumberPagination` with 20 items per page on all list endpoints.

```json
{ "count": 100, "next": "...", "previous": "...", "results": [] }
```

---

## Testing

```bash
python manage.py test --verbosity=2
```

### Coverage — 51 tests total

| App | Tests | Coverage |
|---|---|---|
| `accounts` | 18 | User model, registration (success/duplicate/mismatch), login (success/wrong/nonexistent), profile, admin user management (list/update/deactivate/self-delete prevention), viewer access denial |
| `records` | 20 | Model soft delete, CRUD with role enforcement, input validation (negative amount, future date, invalid type), filtering (type, date range, category, amount range), search |
| `dashboard` | 13 | Access control for all 4 endpoints (viewer denied, analyst allowed, admin allowed, unauthenticated denied), summary calculation correctness, date filtering, empty data, category grouping, monthly trends, recent activity limit |

---

## Default Credentials

| Role | Email | Password |
|---|---|---|
| Admin | `admin@finance.local` | `admin123456` |

Create via:

```bash
python manage.py seed_admin
```