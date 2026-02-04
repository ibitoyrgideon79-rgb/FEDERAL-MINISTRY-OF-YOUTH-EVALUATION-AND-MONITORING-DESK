# Digital Monitoring Tool (DMT) Backend

A FastAPI backend with OTP email authentication, SQLite + SQLAlchemy, and simple session-based auth.

Setup
1. Copy `.env.example` to `.env` and fill in SMTP/DATABASE settings.
2. pip install -r requirements.txt
3. Run with: uvicorn main:app --reload

Features
- Request OTP by email and verify to login
- Session cookie-based authentication (session token stored in a secure cookie)
- Admin user: set ADMIN_EMAIL in your .env to grant admin role to that email
- Create and fetch monthly reports (users can access their own reports; admin can access all)
- Dashboard aggregation
- Programmes list (preloaded)
