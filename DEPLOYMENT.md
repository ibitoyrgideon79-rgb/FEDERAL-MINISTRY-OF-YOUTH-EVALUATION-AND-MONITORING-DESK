# Digital Monitoring Tool (DMT) - Vercel Deployment Guide

## Quick Start (Local Development)

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Run the server
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Open http://localhost:8000 in your browser.

---

## Deployment to Vercel

### Prerequisites
1. **Vercel Account** - Sign up at https://vercel.com
2. **GitHub Repository** - Push your code to GitHub
3. **PostgreSQL Database** - Use one of:
   - Neon (https://neon.tech) - Free tier available
   - Supabase (https://supabase.com) - Free tier available
   - Railway (https://railway.app) - Free tier available
   - AWS RDS
   - Digital Ocean

### Step-by-Step Deployment

#### 1. Set Up PostgreSQL Database

**Option A: Using Neon (Recommended)**
1. Go to https://neon.tech and sign up
2. Create a new project
3. Copy the connection string (looks like: `postgresql://user:password@ep-xxxxx.neon.tech/dbname`)
4. Keep it safe for the next steps

**Option B: Using Supabase**
1. Go to https://supabase.com and sign up
2. Create a new project
3. Go to Settings → Database → Connection Pooling
4. Copy the connection string
5. Replace `[YOUR-PASSWORD]` with your actual password

#### 2. Push Code to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/dmt.git
git push -u origin main
```

#### 3. Deploy to Vercel

1. Go to https://vercel.com and sign in
2. Click "New Project"
3. Import your GitHub repository
4. Select "Other" as framework (it will auto-detect Python)
5. Configure Environment Variables:
   - `DATABASE_URL`: Your PostgreSQL connection string
   - `ADMIN_EMAIL`: Your admin email address
   - `EMAIL_BACKEND`: `console` or `smtp`
   - `SMTP_HOST`: (e.g., `smtp.gmail.com`)
   - `SMTP_PORT`: `587`
   - `SMTP_USERNAME`: Your email
   - `SMTP_PASSWORD`: Your app-specific password
   - `FROM_EMAIL`: Your email address
   - `SESSION_EXPIRE_DAYS`: `30`

6. Click "Deploy"

#### 4. Run Database Migrations

After deployment:

1. Clone your Vercel deployment locally for testing
2. Set environment variables in local .env
3. Run the database initialization:
   ```bash
   python -c "from database import engine, Base; Base.metadata.create_all(bind=engine)"
   ```
4. Optionally seed data:
   ```bash
   python -c "from database import SessionLocal; from programmes import preload_programmes; db = SessionLocal(); preload_programmes(db); print('Programmes loaded!')"
   ```

Or use Vercel's Python runtime to run these commands in a serverless function.

---

## Setting Up Gmail for Email Notifications

1. Enable 2-Factor Authentication on your Gmail account
2. Generate an App Password:
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" and "Windows Computer"
   - Google will generate a 16-character password
   - Use this as `SMTP_PASSWORD`

3. Use these settings:
   - `SMTP_HOST`: `smtp.gmail.com`
   - `SMTP_PORT`: `587`
   - `SMTP_USERNAME`: Your Gmail address
   - `SMTP_PASSWORD`: The 16-character app password

---

## Features After Deployment

✅ Email OTP Authentication
✅ Role-based Access (Admin/User)
✅ Monthly Report Submission
✅ Analytics Dashboard with Charts
✅ Report Export to Excel
✅ Auto-notifications to Admins
✅ Session-based Auth with Cookies

---

## Troubleshooting

### "Database connection failed"
- Verify DATABASE_URL is correct
- Check if database is publicly accessible
- Ensure IP whitelist includes Vercel's IPs (usually unrestricted for Neon/Supabase)

### "Module not found" errors
- Ensure all dependencies are in `requirements.txt`
- Rebuild the project on Vercel (Deployments → Redeploy)

### "Email not sending"
- Check SMTP credentials are correct
- Verify "Less secure app access" is enabled (if using Gmail)
- Check console/mail backend setting matches your config

### "Reports not showing"
- Verify DATABASE_URL is set correctly
- Check logs in Vercel dashboard
- Manually seed data after first deployment

---

## API Endpoints

### Authentication
- `POST /auth/request-otp` - Request OTP
- `POST /auth/verify-otp` - Verify OTP & Login
- `POST /auth/logout` - Logout

### Reports
- `POST /reports/` - Submit report
- `GET /reports/` - Get user's reports (or all if admin)
- `GET /reports/dashboard` - Get dashboard stats

### Programmes
- `GET /programmes/` - Get all programmes

### Notifications
- `POST /notifications/send-reminders` - Send monthly reminders
- `POST /notifications/notify-challenges` - Alert on challenges

---

## Frontend URLs After Deployment

- Login: `https://your-domain.vercel.app/`
- Dashboard: `https://your-domain.vercel.app/dashboard.html`
- Admin: `https://your-domain.vercel.app/admin.html`
- Analytics: `https://your-domain.vercel.app/analytics.html`
- Report Form: `https://your-domain.vercel.app/report-form.html`

---

## Performance Notes

- First request may be slow (cold start)
- Database queries are optimized with SQLAlchemy
- Static files (HTML/CSS/JS) are served with Vercel CDN
- Consider adding caching headers for static assets

---

## Production Checklist

- [ ] DATABASE_URL configured with production database
- [ ] ADMIN_EMAIL set to your email
- [ ] Email credentials configured (SMTP settings)
- [ ] Session expire days set appropriately
- [ ] API is accessible from frontend domain
- [ ] CORS is properly configured
- [ ] Test login, report submission, and analytics
- [ ] Test email notifications
- [ ] Monitor Vercel logs for errors

---

## Support

For issues or questions:
1. Check Vercel logs: Dashboard → Project → Deployments → Logs
2. Check browser console (F12) for frontend errors
3. Test locally first before deploying

Happy monitoring! 🚀
