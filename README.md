# 🔗 Django URL Shortener

> A production-inspired backend system built with Django, focused on traffic control, abuse prevention, and scalable URL redirection architecture.

This project goes beyond basic CRUD — it demonstrates real backend engineering patterns including custom middleware, heuristic abuse detection, and concurrency-safe database operations.

---

## 🚀 Features at a Glance

| Feature | Details |
|---|---|
| URL Shortening | Collision-safe short code generation, persistent MySQL storage |
| Rate Limiting | Custom IP-based middleware, sliding window algorithm, HTTP 429 |
| Abuse Detection | Heuristic scoring engine, burst & anomaly detection, HTTP 403 |
| Click Analytics | Atomic counter increments per redirect using Django F() expressions |
| Clean Architecture | Views / Models / Middleware / Utils / Abuse Detection fully separated |

---

## 🏗️ System Design

```
Client Request
      │
      ▼
Rate Limit Middleware     ← Sliding window, per-IP, per-endpoint limits
      │
      ▼
Abuse Detection Engine    ← Heuristic scoring: frequency, URL length, domain depth
      │
      ▼
Business Logic (Views)    ← Validation, short code generation
      │
      ▼
MySQL Database            ← Atomic click increments, persistent storage
```

**Redirect flow:**

```
Short URL → DB Lookup → Atomic Click Increment (F expression) → 301 Redirect
```

---

## 📁 Project Structure

```
url_shortener/
├── url_shortener/
│   ├── settings.py
│   └── urls.py
│
└── shortener/
    ├── middleware/
    │   └── rate_limit.py       # Custom sliding window rate limiter
    ├── models.py               # ShortURL model
    ├── views.py                # API endpoints
    ├── urls.py                 # Route definitions
    ├── utils.py                # Short code generator
    └── abuse_detector.py       # Heuristic scoring engine
```

---

## 🔐 Rate Limiting — Custom Middleware

Built entirely from scratch with no third-party libraries.

**Strategy:** Sliding window using in-memory IP-based timestamp tracking.

```python
LIMITS = {
    "/create/": 10,    # Strict limit — creation endpoint
    "/r/":      100,   # Higher limit — redirect endpoint
}
TIME_WINDOW = 60  # seconds
```

**How it works:**

1. Each incoming request is tagged to a client IP
2. Timestamps older than 60 seconds are discarded
3. If the rolling count exceeds the endpoint's limit, the request is rejected
4. Otherwise, the timestamp is logged and the request proceeds

**Response on limit breach:**
```json
HTTP 429 — Too Many Requests
{ "error": "Rate limit exceeded. Try again later." }
```

> **Note:** Currently uses in-memory storage (`defaultdict`), which is intentionally simple for this implementation. The architecture is Redis-ready — swapping in a Redis backend would enable persistence and horizontal scaling across multiple server instances.

---

## 🚨 Abuse Detection Engine

Every `POST /create/` request is evaluated by a heuristic scoring engine before the short URL is created.

| Rule | Trigger | Score |
|---|---|---|
| High request frequency | > 5 requests in 60s | +30 |
| Extremely long URL | length > 200 characters | +20 |
| Suspicious domain depth | > 3 subdomains | +20 |
| Burst behavior | > 3 requests in window | +10 |

**Abuse threshold: 60 points**

If the score meets or exceeds the threshold:

```json
HTTP 403 — Forbidden
{ "error": "Abusive behavior detected" }
```

This mimics basic bot protection used in production SaaS platforms, making decisions based on behavioral signals rather than static blocklists.

---

## 📊 API Endpoints

### `POST /create/`

Creates a shortened URL.

**Request (JSON or form-data):**
```json
{ "url": "https://example.com/some/very/long/path" }
```

**Response:**
```json
{ "short-url": "http://127.0.0.1:8000/r/aB3xYz" }
```

**Error cases:**
- `400` — Missing or malformed URL
- `403` — Abuse detected
- `429` — Rate limit exceeded

---

### `GET /r/<short_code>/`

Redirects to the original URL and increments the click counter atomically.

```python
ShortURL.objects.filter(id=url.id).update(clicks=F('clicks') + 1)
```

Using Django's `F()` expression avoids race conditions by pushing the increment to the database level instead of reading and writing in application memory.

**Error cases:**
- `404` — Short code not found

---

## 🛠️ Setup & Installation

**Prerequisites:** Python 3.10+, MySQL

```bash
# Clone the repo
git clone https://github.com/yourusername/url-shortener.git
cd url-shortener

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install django djangorestframework mysqlclient

# Configure database in settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'url_shortener_db',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Start server
python manage.py runserver
```

---

## 🧠 Engineering Decisions

**Why a custom middleware instead of a library like django-ratelimit?**
Building it from scratch demonstrates understanding of Django's middleware lifecycle, sliding window algorithms, and IP extraction — and avoids a dependency for logic that is straightforward to own.

**Why F() expressions for click counts?**
`update(clicks=F('clicks') + 1)` issues a single atomic SQL `UPDATE`, preventing lost increments when multiple requests hit the same short code simultaneously.

**Why heuristic scoring instead of a static blocklist?**
Scoring lets the system catch novel abuse patterns (burst behavior, unusual URL shapes) that a fixed blocklist would miss, without manual curation.

---

## 🔮 What a Production Version Would Add

- **Redis** for distributed, persistent rate limiting and abuse tracking across server instances
- **Authentication** — user accounts with per-user link management
- **Link expiry** — TTL support on short codes
- **Async redirects** — non-blocking click count updates via Celery
- **Structured logging** — per-request audit trail for security review
- **Docker + environment config** — remove hardcoded credentials from settings

---

## 👩‍💻 Author

**Karthika U** — Backend Engineer

Python · Django · System Design · API Development
