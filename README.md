# 🔗 Django URL Shortener with Smart Rate Limiting & Abuse Detection

A production-grade backend system built using Django + DRF, designed to simulate real-world traffic control, abuse prevention, and scalable URL redirection systems.

This project demonstrates backend engineering beyond CRUD, focusing on:

 ✅Traffic shaping

 ✅Security heuristics

 ✅Distributed system patterns.

## 🔥 Why This Project Stands Out
 **🚀 End-to-End URL Shortening Pipeline**
Convert long URLs into compact short links with collision-safe generation and persistent MySQL storage.

🔐 Custom Rate Limiting Middleware (From Scratch)

✅No third-party libraries — fully handcrafted.

✅ IP-based request tracking

✅ Maximum 50 requests per minute

✅ Automatic blocking of abusive traffic

✅ Returns HTTP 429 (Too Many Requests)

✅ Simulates real production throttling systems.

## Intelligent Abuse Detection Engine

Every request is evaluated using **heuristic** scoring to detect malicious behavior:

✔ Excessive request frequency

✔ Suspicious domain patterns

✔ Extremely long URLs

✔ Burst traffic activity

When thresholds are exceeded:

👉 IP is instantly blocked with HTTP 403 (Forbidden)

This mimics basic bot protection used in real SaaS platforms.

## 📊 Redirection + Analytics

Short URLs redirect to original destinations

Each redirect increments a click counter

Enables basic traffic analytics per link

## 🏗 Clean Modular Architecture

Clear separation of responsibilities:

✅ Views

✅ Models

✅ Middleware

✅ Utilities

✅ Abuse Detection Logic

Promotes maintainability and scalability.

## 🧠 System Design Overview
```
Client Request
      |
      v
Rate Limit Middleware
      |
      v
Abuse Detection Engine
      |
      v
Create Short URL API
      |
      v
MySQL Database
```

**Redirect Flow:**

Short URL → Database Lookup → Increment Click Count → Redirect

## 📁 Project Structure
```
shortener/
│
├── middleware/
│   └── rate_limit.py
├── models.py
├── views.py
├── urls.py
├── utils.py
├── abuse_detector.py
│
url_shortener/
├── settings.py
├── urls.py
│
manage.py
README.md
```

## 🔐 Rate Limiting Strategy
- Implemented using Redis
- Sliding window / token bucket approach
Each IP maintains a rolling window of timestamps:

Requests older than 60 seconds are discarded

New requests are added to memory

If count exceeds 50/min, request is rejected

RATE_LIMIT = 50

TIME_WINDOW = 60


**Response:**

**HTTP 429 – Too Many Requests**

Why Redis?
- Fast in-memory access
- Atomic operations
Scaling:
- Stateless API servers
- Centralized Redis
## 🚨 Abuse Detection Rules

Each request is scored based on:

• Request frequency

• URL length anomalies

• Suspicious domain depth

• Burst behavior

**If abuse score exceeds threshold:**

**HTTP 403 – Abusive Behavior Detected**


## 👩‍💻 Author

**Karthika U**

Aspiring Backend Engineer | Python | Django | System Design

---
