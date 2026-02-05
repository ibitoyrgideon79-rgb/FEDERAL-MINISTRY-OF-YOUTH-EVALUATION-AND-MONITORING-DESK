# Vercel Deployment Checklist

## Pre-Deployment (Local)

- [ ] All code committed to GitHub
- [ ] No .env file with secrets committed (only .env.example)
- [ ] Tested locally with `python -m uvicorn main:app --reload`
- [ ] All features working:
  - [ ] Login with OTP
  - [ ] Report submission
  - [ ] Admin dashboard
  - [ ] Analytics
  - [ ] Email notifications

## PostgreSQL Setup (Choose One)

### Option 1: Neon (Recommended)
- [ ] Created account at https://neon.tech
- [ ] Created new project
- [ ] Copied connection string
- [ ] Connection string format: `postgresql://user:password@host:port/dbname`

### Option 2: Supabase
- [ ] Created account at https://supabase.com
- [ ] Created new project
- [ ] Found connection string in Settings → Database → Connection Pooling
- [ ] Replaced `[YOUR-PASSWORD]` with actual password

### Option 3: Railway/Other
- [ ] Database created
- [ ] Connection string obtained
- [ ] Port and credentials verified

## Vercel Deployment

- [ ] Vercel account created
- [ ] Project imported from GitHub
- [ ] Python runtime selected (auto-detected)
- [ ] Environment variables configured:
  - [ ] `DATABASE_URL` = PostgreSQL connection string
  - [ ] `ADMIN_EMAIL` = Your email
  - [ ] `EMAIL_BACKEND` = `console` or `smtp`
  - [ ] `SMTP_HOST` = (if using SMTP)
  - [ ] `SMTP_PORT` = (if using SMTP)
  - [ ] `SMTP_USERNAME` = (if using SMTP)
  - [ ] `SMTP_PASSWORD` = (if using SMTP)
  - [ ] `FROM_EMAIL` = Your email
  - [ ] `SESSION_EXPIRE_DAYS` = `30`
- [ ] Deployment successful (no errors in logs)

## Post-Deployment

- [ ] Application loads at Vercel URL
- [ ] Database initialized (first request may be slow)
- [ ] Can login with test account
- [ ] Can submit report
- [ ] Report appears in dashboard
- [ ] Admin receives email notification
- [ ] Analytics dashboard shows data
- [ ] Can export reports as Excel

## Email Setup (if using SMTP)

- [ ] Gmail account with 2FA enabled
- [ ] App-specific password generated
- [ ] Added to Vercel environment variables
- [ ] Tested by submitting a report

## Monitoring

- [ ] Check Vercel logs regularly: https://vercel.com/dashboard
- [ ] Monitor database usage/limits
- [ ] Test email delivery occasionally
- [ ] Check for any 500 errors

## Custom Domain (Optional)

- [ ] Domain purchased
- [ ] DNS configured to point to Vercel
- [ ] SSL certificate auto-generated
- [ ] HTTPS working

## Troubleshooting Commands

If deployment fails, check:

```bash
# View Vercel deployment logs
vercel logs --tail

# Test database connection locally
python -c "from database import engine; print(engine)"

# Check Python version
python --version

# Verify requirements.txt
cat requirements.txt
```

---

**Deployment Date**: ___________
**Deployed URL**: ___________
**Database Provider**: ___________
**Notes**: ___________
