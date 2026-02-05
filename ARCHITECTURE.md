# DMT Architecture & Deployment Diagram

## Local Development Setup

```
Your Computer
└── VS Code
    └── DMT Project
        ├── Backend: FastAPI (main.py)
        │   ├── Models (SQLAlchemy)
        │   ├── Routes (Auth, Reports, etc)
        │   └── Utils (Email, Security)
        │
        ├── Frontend: HTML/CSS/JS
        │   ├── index.html (Login)
        │   ├── dashboard.html (User Dashboard)
        │   ├── admin.html (Admin Panel)
        │   └── analytics.html (Charts)
        │
        └── Database: SQLite (dmt.db)
            └── Local testing only

Server: http://localhost:8000
```

---

## Vercel Deployment Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    GitHub (Code Storage)                │
│  Your repo with all code and configuration files        │
│  - vercel.json                                          │
│  - requirements.txt                                     │
│  - .env.example (no secrets!)                           │
└────────────┬────────────────────────────────────────────┘
             │ Auto-deploy on push
             ▼
┌─────────────────────────────────────────────────────────┐
│                  Vercel CDN (Edge Network)              │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │         FastAPI Python Runtime                   │  │
│  │                                                  │  │
│  │  ┌─────────────────────────────────────────┐   │  │
│  │  │  API Routes                             │   │  │
│  │  │  - POST /auth/request-otp               │   │  │
│  │  │  - POST /auth/verify-otp                │   │  │
│  │  │  - POST /reports/                       │   │  │
│  │  │  - GET /reports/                        │   │  │
│  │  │  - GET /programmes/                     │   │  │
│  │  │  - GET /analytics/ (via dashboard)      │   │  │
│  │  └──────────────┬──────────────────────────┘   │  │
│  │                 │                               │  │
│  │  ┌──────────────▼──────────────────────────┐   │  │
│  │  │  Static File Server (HTML/CSS/JS)       │   │  │
│  │  │  - /index.html                          │   │  │
│  │  │  - /dashboard.html                      │   │  │
│  │  │  - /admin.html                          │   │  │
│  │  │  - /analytics.html                      │   │  │
│  │  │  - /style.css                           │   │  │
│  │  │  - /*.js files                          │   │  │
│  │  └─────────────────────────────────────────┘   │  │
│  │                                                  │  │
│  │  Environment Variables (Secure)                │  │
│  │  - DATABASE_URL (encrypted)                    │  │
│  │  - SMTP credentials (encrypted)                │  │
│  │  - ADMIN_EMAIL (encrypted)                     │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  URL: https://dmt.vercel.app (or your domain)         │
└──────────┬──────────────────────────────────────────────┘
           │
           │ Network requests
           │
    ┌──────▼──────────────────────────────────────────────┐
    │         PostgreSQL Database (Neon/Supabase)        │
    │                                                     │
    │  Tables:                                           │
    │  ├── users (email, role, created_at)             │
    │  ├── otp (email, code, expires_at, used)         │
    │  ├── sessions (token, user_id, expires_at)       │
    │  ├── programmes (name, department)               │
    │  └── monthly_reports (all report data)           │
    │                                                     │
    │  Connection: postgresql://user:pass@host/dmt      │
    └────────────────────────────────────────────────────┘
```

---

## Data Flow: Report Submission

```
1. USER SUBMITS REPORT
   │
   └─► /report-form.html (Frontend)
       │
       └─► Form validation (JavaScript)
           │
           └─► POST /reports/ (FastAPI)
               │
               ├─► Validate data (Pydantic)
               │
               ├─► Save to Database
               │   └─► PostgreSQL: monthly_reports table
               │
               ├─► Query admins from database
               │
               ├─► Send email notifications
               │   └─► SMTP to Gmail server
               │
               └─► Return report data (JSON)
                   │
                   └─► Frontend shows success message
                       │
                       └─► Redirect to /dashboard.html
                           │
                           └─► GET /reports/ loads all user reports
                               │
                               └─► Display reports in table
```

---

## Authentication Flow

```
1. USER ENTERS EMAIL
   │
   └─► /index.html (Login page)
       │
       └─► POST /auth/request-otp
           │
           ├─► Generate 6-digit OTP
           │
           ├─► Save OTP with 5-min expiry
           │
           ├─► Send via email (SMTP)
           │
           └─► Return: "Check your email"

2. USER ENTERS OTP
   │
   └─► POST /auth/verify-otp
       │
       ├─► Validate OTP code
       │
       ├─► Create/update user
       │   └─► If email matches ADMIN_EMAIL → set role="admin"
       │
       ├─► Create session token
       │
       ├─► Set session cookie (HttpOnly)
       │
       └─► Redirect to /dashboard.html
           │
           └─► User logged in ✅
```

---

## Email Notification System

```
Report Submitted
└─► Backend checks for admins
    │
    └─► For each admin email:
        │
        ├─► Create email subject
        │
        ├─► Format email body with report data
        │
        ├─► Connect to SMTP server (Gmail)
        │   │
        │   └─► Authentication: email + app-password
        │
        └─► Send email
            │
            └─► Admin receives notification ✅
```

---

## Deployment Process

```
Step 1: Code on GitHub
├─ Commit code: git push origin main
└─► GitHub repository ready

Step 2: Connect to Vercel
├─ Import GitHub repo into Vercel
└─► Vercel watches for changes

Step 3: Configure Environment
├─ Add DATABASE_URL
├─ Add EMAIL credentials
├─ Add ADMIN_EMAIL
└─► Vercel stores securely

Step 4: Vercel Deploys
├─ Detects Python project
├─ Installs dependencies from requirements.txt
├─ Runs FastAPI on Vercel serverless
├─ Mounts static files (frontend)
└─► App is LIVE ✅

Step 5: Auto-Deploy on Updates
├─ You: git push
├─ GitHub: updates repo
├─ Vercel: auto-detects change
├─ Vercel: rebuilds & redeploys
└─► Updates live instantly ✅
```

---

## Performance Timeline

```
User Action          Time        Location
─────────────────────────────────────────────────
Click Login           0ms        Browser
├─ Fetch /index.html  100ms      Vercel CDN
├─ Load CSS/JS        150ms      Vercel CDN
└─ Page Ready         250ms      Browser ✅

Enter Email & OTP     0ms        Browser
├─ POST /auth/request-otp
│   ├─ Generate code  50ms       Python Runtime
│   ├─ Save to DB     100ms      PostgreSQL
│   ├─ Send email     500ms      Gmail SMTP
│   └─ Response       650ms      Browser
└─ OTP Email Received 1-5s       User's inbox

Verify OTP            0ms        Browser
├─ POST /auth/verify-otp
│   ├─ Validate       30ms       Python Runtime
│   ├─ Create session 50ms       PostgreSQL
│   ├─ Set cookie     10ms       HTTP
│   └─ Response       90ms       Browser
└─ Logged In ✅       150ms      Dashboard

Submit Report         0ms        Browser
├─ POST /reports/
│   ├─ Validate       50ms       Python
│   ├─ Save report    100ms      PostgreSQL
│   ├─ Query admins   30ms       PostgreSQL
│   ├─ Send email     400ms      Gmail SMTP
│   └─ Response       580ms      Browser
└─ Redirect & Reload  800ms      Dashboard ✅
```

---

## Security Layers

```
Frontend
├─ HTTPS enforced (Vercel)
├─ HttpOnly cookies (no JS access)
└─ CORS configured for API routes

Backend
├─ Input validation (Pydantic)
├─ Session tokens validated
├─ Role-based access control
├─ SQL injection prevention (SQLAlchemy ORM)
└─ Environment variables encrypted (Vercel)

Database
├─ PostgreSQL (industry standard)
├─ Connection string encrypted
├─ No direct internet access (firewall)
├─ Regular backups (provider maintained)
└─ SSL connections only

Email
├─ App-specific passwords (Gmail)
├─ TLS/SSL encryption (SMTP)
└─ No plaintext credentials in code
```

---

## Infrastructure Costs

```
Component                Free Tier           Annual Cost
──────────────────────────────────────────────────────
Vercel Hosting           ✅ Yes              $0
  - Compute              Up to 100 GB/month
  - Bandwidth            Generous
  - Build time           Limited

PostgreSQL (Neon)        ✅ Yes              $0
  - Storage              Up to 3 GB
  - Connections          Up to 20

Email (Gmail SMTP)       ✅ Yes              $0
  - Emails/day           ~2000
  - Attachments          Yes

GitHub                   ✅ Yes              $0
  - Public repos         Unlimited
  - Private repos        Unlimited

CDN (Vercel Built-in)    ✅ Yes              $0
  - Global edge          Included
  - Caching              Included

──────────────────────────────────────────────────────
TOTAL (Startup)                             $0/month

Scaling (when you exceed limits):
  - Vercel Pro           $20/month
  - Neon Advanced Plan   $50+/month
  - Enterprise features  Custom pricing
```

---

## Monitoring & Alerts

```
Vercel Dashboard
├─ Deployment logs
├─ Error rates
├─ Build times
├─ API performance
└─ Traffic insights

Neon Dashboard
├─ Database connections
├─ Query performance
├─ Storage usage
└─ Backup status

Email Monitoring
├─ Gmail delivery status
├─ Bounce rates
└─ Spam folder checks

Application Logs
├─ Authentication events
├─ Report submissions
├─ API errors
└─ Database queries
```

---

## Scaling Path

```
Phase 1: MVP (Now)
├─ 1-10 users
├─ ~1 report/user/month
├─ Neon Free + Vercel Free
└─ Cost: $0/month

Phase 2: Growth (100 users)
├─ 50-100 active users
├─ ~5 reports/user/month
├─ Neon +3GB upgrade
├─ Vercel Pro ($20/month)
└─ Cost: ~$50-70/month

Phase 3: Scale (1000+ users)
├─ 500+ active users
├─ ~10 reports/user/month
├─ Dedicated PostgreSQL server
├─ Vercel Enterprise
├─ API rate limiting needed
└─ Cost: $500+/month (negotiable)
```

---

This architecture is designed to be:
✅ Scalable - Easy to upgrade when needed
✅ Secure - Industry best practices
✅ Cost-effective - Free to start
✅ Maintainable - Standard tools & frameworks
✅ Reliable - 99.95% uptime SLA

