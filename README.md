# SokoPoint — Project Documentation

**Version:** 1.0.0  
**Framework:** Django 5.2 + Django REST Framework 3.16  
**Database:** SQLite (Django ORM)  
**Auth:** Custom User + JWT (SimpleJWT)

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Tech Stack](#2-tech-stack)
3. [Project Structure](#3-project-structure)
4. [Models & Database](#4-models--database)
5. [Authentication](#5-authentication)
6. [Vendor Workflow](#6-vendor-workflow)
7. [Customer Workflow](#7-customer-workflow)
8. [REST API Reference](#8-rest-api-reference)
9. [Permissions & Security](#9-permissions--security)
10. [Validation Rules](#10-validation-rules)
11. [Running the Project](#11-running-the-project)

---

## 1. Project Overview

SokoPoint is a multi-vendor e-commerce marketplace built with Django. It supports two types of users — **Vendors** (sellers) and **Customers** (buyers) — and exposes a full **REST API** with JWT authentication for programmatic access.

**Key Features:**
- Multi-vendor product listings
- Session-based shopping cart
- Multi-step checkout (COD, Card, Mobile Money)
- Order management with status tracking
- JWT-secured REST API
- Interactive Swagger API documentation

---

## 2. Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend Framework | Django 5.2 |
| REST API | Django REST Framework 3.16 |
| Authentication | JWT via `djangorestframework-simplejwt` |
| API Documentation | `drf-spectacular` (OpenAPI 3 / Swagger) |
| Filtering | `django-filter` |
| Database | SQLite (via Django ORM) |
| Media/Images | Pillow |
| Password Hashing | Django PBKDF2 + validators |

---

## 3. Project Structure

```
SokoPoint/
│
├── manage.py
├── db.sqlite3
│
├── SokoPoint/              ← Project config
│   ├── settings.py
│   ├── urls.py             ← Root URL router
│   └── views.py            ← Homepage view
│
├── account/                ← User management app
│   ├── models.py           ← CustomUser model
│   ├── forms.py            ← Register/Login forms
│   ├── views.py            ← Web views (HTML)
│   ├── api_views.py        ← DRF API views
│   └── urls.py
│
├── product/                ← Product management app
│   ├── models.py           ← Product model
│   ├── form.py             ← ProductForm
│   ├── views.py            ← Web views (HTML)
│   └── urls.py
│
├── cart/                   ← Shopping cart app
│   ├── cart.py             ← Cart class (session-based)
│   ├── views.py            ← Add/Remove/View cart
│   └── urls.py
│
├── order/                  ← Order & payment app
│   ├── models.py           ← Order, OrderItem, Payment
│   ├── forms.py            ← Checkout, Payment forms
│   ├── views.py            ← Checkout workflow
│   └── urls.py
│
└── api/                    ← Central DRF API app
    ├── serializers.py      ← All DRF serializers
    ├── views.py            ← API views
    └── urls.py             ← API routes
```

---

## 4. Models & Database

### 4.1 CustomUser (`account`)

```python
class CustomUser(AbstractBaseUser, PermissionsMixin):
    username    = CharField(unique=True)
    first_name  = CharField
    last_name   = CharField
    email       = EmailField(unique=True)
    phone       = CharField(unique=True)
    location    = CharField
    user_type   = CharField  # 'customer' | 'vendor'
    is_staff    = BooleanField
    is_active   = BooleanField
    date_joined = DateTimeField
```

**Custom Manager:** `CustomUserManager`  
- `create_user()` — validates password strength  
- `create_superuser()` — sets `is_staff=True`, `is_superuser=True`

---

### 4.2 Product (`product`)

```python
class Product(models.Model):
    vendor      = ForeignKey(CustomUser)  # related_name='products'
    name        = CharField(max_length=100)
    price       = DecimalField(max_digits=10)
    currency    = CharField  # USD | RWF | EUR | KES
    description = TextField
    unit        = CharField  # kg | pcs | lit | bag | box | ...
    image       = ImageField(upload_to='product_images/')
    status      = BooleanField(default=True)
    created_at  = DateTimeField(auto_now_add=True)
    updated_at  = DateTimeField(auto_now=True)
```

---

### 4.3 Order (`order`)

```python
class Order(models.Model):
    customer         = ForeignKey(CustomUser)  # related_name='orders'
    total_amount     = DecimalField
    status           = CharField  # PENDING | PROCESSING | SHIPPED | DELIVERED | CANCELLED
    delivery_address = TextField
    district         = CharField  # One of 30 Rwanda districts
    phone_number     = CharField
    created_at       = DateTimeField(auto_now_add=True)
    updated_at       = DateTimeField(auto_now=True)
```

---

### 4.4 OrderItem (`order`)

```python
class OrderItem(models.Model):
    order    = ForeignKey(Order)    # related_name='order_items'
    product  = ForeignKey(Product)  # related_name='order_items'
    quantity = IntegerField
    price    = DecimalField         # snapshot of price at time of order
```

---

### 4.5 Payment (`order`)

```python
class Payment(models.Model):
    order                 = ForeignKey(Order)  # related_name='payments'
    amount                = DecimalField
    status                = CharField   # PENDING | COMPLETED | FAILED
    payment_method        = CharField   # MOBILE_MONEY | CARD | CASH_ON_DELIVERY
    transaction_reference = CharField   # UUID, set on success
    created_at            = DateTimeField(auto_now_add=True)
    updated_at            = DateTimeField(auto_now=True)
```

---

### Entity Relationship

```
CustomUser ──< Product         (vendor owns many products)
CustomUser ──< Order           (customer places many orders)
Order      ──< OrderItem       (one order has many items)
Product    ──< OrderItem       (one product in many order items)
Order      ──< Payment         (one order has one payment)
```

---

## 5. Authentication

### Web Authentication (Django Sessions)

| Action | URL | Method |
|--------|-----|--------|
| Register Customer | `/account/register/customer/` | GET/POST |
| Register Vendor | `/account/register/vendor/` | GET/POST |
| Login | `/account/login/` | GET/POST |
| Logout | `/account/logout/` | GET |

Login logic:
```python
user = authenticate(username=username, password=password)
if user.user_type == 'vendor':
    redirect('vendor_dashboard')
else:
    redirect('customer_dashboard')
```

---

### API Authentication (JWT)

| Action | URL | Method |
|--------|-----|--------|
| Get tokens | `/api/auth/login/` | POST |
| Refresh token | `/api/auth/refresh/` | POST |

**Step 1 — Login:**
```http
POST /api/auth/login/
Content-Type: application/json

{
  "username": "john",
  "password": "SecurePass123!"
}
```

**Response:**
```json
{
  "access":  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Step 2 — Use the token on every authenticated request:**
```http
GET /account/api/profile/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Step 3 — Refresh when expired (after 60 minutes):**
```http
POST /api/auth/refresh/
Content-Type: application/json

{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Token Lifetimes:**
- Access token: **60 minutes**
- Refresh token: **1 day**

---

## 6. Vendor Workflow

### Step 1 — Register
`POST /account/register/vendor/`

```
Fields:  username, email, phone, location, password, confirm_password
Result:  user_type set to 'vendor'
After:   Redirected to login
```

### Step 2 — Login
`POST /account/login/`

```
After:   Redirected to /account/vendor/dashboard/
```

### Step 3 — Vendor Dashboard
`GET /account/vendor/dashboard/`

Shows all products belonging to this vendor.

### Step 4 — Add Product
`GET/POST /product/add/`

```
Fields:  name, price, currency, description, unit, image, status
Auto:    product.vendor = logged-in user
After:   Redirected to vendor dashboard
```

### Step 5 — Edit Product
`GET/POST /product/<id>/edit/`

```
Guard:   user must be the product's vendor
```

### Step 6 — Delete Product
`GET/POST /product/<id>/delete/`

```
Guard:   user must be the product's vendor
After:   Redirected to vendor dashboard
```

### Step 7 — View Orders
`GET /order/vendor/`

Shows all orders that contain this vendor's products.

### Step 8 — Confirm/Ship Order
`POST /order/vendor/confirm/<order_id>/`

```
Guard:   order must contain vendor's product
Action:  status PROCESSING → SHIPPED
```

**Order Status Flow:**
```
PENDING ──► PROCESSING ──► SHIPPED ──► DELIVERED
                │
                └──► CANCELLED
```

---

## 7. Customer Workflow

### Step 1 — Register
`POST /account/register/customer/`

```
Fields:  username, first_name, last_name, email, phone, location, password, confirm_password
Result:  user_type set to 'customer'
```

### Step 2 — Login
`POST /account/login/`

```
After:   Redirected to /account/customer/dashboard/
```

### Step 3 — Browse Products
`GET /account/customer/dashboard/` or `GET /product/`

Shows all active products from all vendors.

### Step 4 — View Product Details
`GET /product/<id>/`

Shows: name, price, currency, unit, description, image, vendor.

### Step 5 — Add to Cart
`POST /cart/add/<product_id>/`

```
Body:    quantity (default: 1)
Storage: Session-based (no database)
After:   Redirected to cart page
```

### Step 6 — View Cart
`GET /cart/`

Shows all items, quantities, prices, and total.

### Step 7 — Remove from Cart
`POST /cart/remove/<product_id>/`

### Step 8 — Checkout
`GET/POST /order/checkout/`

```
Guard:   Cart must not be empty
Fields:  phone_number, district (30 choices), delivery_address, payment_method
Creates: Order (PENDING) + OrderItems + Payment (PENDING)
After:   Redirected to payment page
```

**Payment Methods:**
| Method | Behaviour |
|--------|-----------|
| Cash on Delivery | Payment instantly COMPLETED, no form needed |
| Card | Enter card_number, expiry, CVV |
| Mobile Money | Choose provider (MTN/Airtel/M-Pesa) + phone |

### Step 9 — Payment
`GET/POST /order/payment/<order_id>/`

On success:
```
Payment.status             → COMPLETED
Payment.transaction_reference → UUID (e.g. "a1b2c3d4-e5f6-...")
Order.status               → PROCESSING
Cart                       → Cleared
```

### Step 10 — Order Confirmation
`GET /order/confirmation/<order_id>/`

### Step 11 — View My Orders
`GET /order/customer/`

---

## 8. REST API Reference

### Base URL
```
http://127.0.0.1:8000
```

### API Documentation (Interactive)
```
http://127.0.0.1:8000/api/docs/       ← Swagger UI
http://127.0.0.1:8000/api/schema/     ← OpenAPI JSON
```

---

### 8.1 Auth Endpoints

#### POST `/api/auth/login/` — Get JWT Tokens
**Request:**
```json
{
  "username": "john_vendor",
  "password": "SecurePass123!"
}
```
**Response `200 OK`:**
```json
{
  "access": "eyJ...",
  "refresh": "eyJ..."
}
```

#### POST `/api/auth/refresh/` — Refresh Access Token
**Request:**
```json
{
  "refresh": "eyJ..."
}
```
**Response `200 OK`:**
```json
{
  "access": "eyJ..."
}
```

---

### 8.2 User Endpoints

#### POST `/account/api/register/` — Register New User
**Request:**
```json
{
  "username": "jane",
  "email": "jane@example.com",
  "phone": "+250788000001",
  "location": "Kigali",
  "user_type": "customer",
  "first_name": "Jane",
  "last_name": "Doe",
  "password": "SecurePass123!",
  "password2": "SecurePass123!"
}
```
**Response `201 Created`:**
```json
{
  "id": 2,
  "username": "jane",
  "email": "jane@example.com",
  "user_type": "customer"
}
```

#### GET/PUT/PATCH `/account/api/profile/` — View or Update Profile
> 🔒 Requires: `Authorization: Bearer <token>`

**GET Response `200 OK`:**
```json
{
  "id": 2,
  "username": "jane",
  "email": "jane@example.com",
  "phone": "+250788000001",
  "location": "Kigali",
  "user_type": "customer",
  "first_name": "Jane",
  "last_name": "Doe",
  "date_joined": "2026-09-15T14:15:00Z"
}
```

---

### 8.3 Serializers Overview

| Serializer | Used For | Key Features |
|-----------|----------|--------------|
| `RegisterSerializer` | User registration | Validates unique email, phone format, password match |
| `UserProfileSerializer` | View/Update profile | Read-only: id, username, user_type, date_joined |
| `ChangePasswordSerializer` | Change password | Validates old password, new password match |
| `ProductSerializer` | CRUD on products | Validates price ≥ 0, vendor auto-assigned |
| `OrderItemSerializer` | Items in an order | Nested inside OrderSerializer |
| `PaymentSerializer` | Order payments | Read-only reference and timestamps |
| `OrderSerializer` | Full order view | Nested items + payments |
| `OrderCreateSerializer` | Place an order | Validates phone, requires ≥1 item |

---

## 9. Permissions & Security

### Web Layer
| View | Guard |
|------|-------|
| All dashboards | `@login_required` |
| Vendor dashboard | `user.user_type == 'vendor'` |
| Customer dashboard | `user.user_type == 'customer'` |
| Edit/Delete product | `product.vendor == request.user` |
| Confirm order | Order must contain vendor's product |
| View my orders | `Order.customer == request.user` |
| Payment page | `Order.customer == request.user` |

### API Layer (DRF Permissions)
| Permission Class | Applied To |
|-----------------|-----------|
| `IsAuthenticated` | Profile, orders, place order |
| `IsAdminUser` | Admin-only endpoints |
| Custom `IsOwner` | Users can only see their own data |
| Custom `IsVendorOrReadOnly` | Only vendor can edit their own products |

---

## 10. Validation Rules

| Field | Rule |
|-------|------|
| `username` | Unique across all users |
| `email` | Unique, valid email format |
| `phone` | 10–15 digits, optional `+` prefix (regex validated) |
| `password` | Min 8 chars, not common, not numeric only |
| `password2` | Must match `password` |
| `price` | Cannot be negative (≥ 0) |
| `quantity` | Must be ≥ 1 |
| `order items` | Order must have at least 1 item |
| `delivery_address` | Required at checkout |
| `district` | Must be one of 30 Rwanda districts |
| `payment_method` | Must be MOBILE_MONEY, CARD, or CASH_ON_DELIVERY |
| `cart` | Must not be empty before checkout |

---

## 11. Running the Project

### Prerequisites
- Python 3.11+
- pip

### Installation

```bash
# 1. Clone the project
cd SokoPoint

# 2. Install dependencies
pip install django djangorestframework djangorestframework-simplejwt django-filter drf-spectacular Pillow

# 3. Run migrations
python manage.py migrate

# 4. Create an admin superuser
python manage.py createsuperuser

# 5. Start the server
python manage.py runserver
```

### Access Points
| URL | Purpose |
|-----|---------|
| http://127.0.0.1:8000/ | Homepage |
| http://127.0.0.1:8000/admin/ | Django Admin |
| http://127.0.0.1:8000/account/register/customer/ | Customer Register |
| http://127.0.0.1:8000/account/register/vendor/ | Vendor Register |
| http://127.0.0.1:8000/account/login/ | Login |
| http://127.0.0.1:8000/api/docs/ | Swagger API Docs |
| http://127.0.0.1:8000/api/auth/login/ | JWT Token Endpoint |

---

## Complete URL Reference

```
Web URLs:
  /                                       → Homepage
  /admin/                                 → Django Admin

  /account/
    register/                             → General registration
    register/customer/                    → Customer registration
    register/vendor/                      → Vendor registration
    login/                                → Login
    logout/                               → Logout
    customer/dashboard/                   → Customer dashboard
    vendor/dashboard/                     → Vendor dashboard
    api/register/                         → API: Register user
    api/login/                            → API: Login
    api/logout/                           → API: Logout
    api/profile/                          → API: View/Update profile
    api/token/                            → JWT obtain pair
    api/token/refresh/                    → JWT refresh

  /product/
    (list)                                → All products
    add/                                  → Add product (vendor)
    <id>/                                 → Product detail
    <id>/edit/                            → Edit product (vendor)
    <id>/delete/                          → Delete product (vendor)

  /cart/
    (view)                                → Cart page
    add/<id>/                             → Add item to cart
    remove/<id>/                          → Remove item from cart

  /order/
    place/<product_id>/                   → Direct single-product order
    checkout/                             → Cart checkout
    payment/<order_id>/                   → Payment form
    confirmation/<order_id>/              → Order success
    customer/                             → My orders (customer)
    vendor/                               → Orders list (vendor)
    vendor/confirm/<order_id>/            → Confirm/ship order (vendor)

API URLs:
  /api/
    schema/                               → OpenAPI schema (JSON)
    docs/                                 → Swagger UI
    auth/login/                           → JWT login
    auth/refresh/                         → JWT refresh
```

---

*SokoPoint — Built with Django & Django REST Framework*  
*Documentation generated: September 2026*
