# 🚀 DMT Vercel Deployment - Complete Guide

## What You Need

1. **GitHub Account** - Free at https://github.com
2. **Vercel Account** - Free at https://vercel.com
3. **PostgreSQL Database** - Free at Neon (https://neon.tech) or Supabase (https://supabase.com)
4. **Gmail Account** - For email notifications (optional but recommended)

---

## 30-Minute Deployment

### Step 1: Push to GitHub (5 minutes)

```bash
cd c:\Users\user\Desktop\DMT

# Create GitHub repo at https://github.com/new

git init
git add .
git commit -m "DMT initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/dmt.git
git push -u origin main
```

### Step 2: Set Up PostgreSQL Database (5 minutes)

**Using Neon (Recommended):**
1. Go to https://neon.tech and sign up
2. Create project → Copy connection string
3. Save for Step 3

**Using Supabase:**
1. Go to https://supabase.com and sign up
2. Create project → Settings → Database → Connection Pooling
3. Copy connection string and replace `[YOUR-PASSWORD]`

### Step 3: Deploy to Vercel (10 minutes)

1. Go to https://vercel.com and sign up/login
2. Click "New Project" → "Import Git Repository"
3. Select your `dmt` repository
4. **Framework**: Leave as default (Python auto-detected)
5. **Environment Variables** - Add these 9 variables:

```
DATABASE_URL = postgresql://user:password@host:port/dmt
ADMIN_EMAIL = your_email@gmail.com
EMAIL_BACKEND = console
SMTP_HOST = smtp.gmail.com
SMTP_PORT = 587
SMTP_USERNAME = your_email@gmail.com
SMTP_PASSWORD = app_specific_password
FROM_EMAIL = your_email@gmail.com
SESSION_EXPIRE_DAYS = 30
```

6. Click "Deploy" → Wait 2-5 minutes
7. ✅ Your app is live at `https://dmt.vercel.app` (custom URL available)

### Step 4: Configure Gmail for Notifications (5 minutes - Optional)

1. Enable 2FA on your Gmail account
2. Go to https://myaccount.google.com/apppasswords
3. Select "Mail" and "Windows Computer"
4. Copy the 16-character password
5. Update `SMTP_PASSWORD` in Vercel environment variables
6. Change `EMAIL_BACKEND` from `console` to `smtp`

### Step 5: Test the Deployment (5 minutes)

```bash
# Test API
python test_deployment.py

# In browser:
# - Login: https://dmt.vercel.app
# - Dashboard: https://dmt.vercel.app/dashboard.html
# - Analytics: https://dmt.vercel.app/analytics.html
```

---

## Key Files for Deployment

| File | Purpose |
|------|---------|
| `vercel.json` | Vercel configuration |
| `requirements.txt` | Python dependencies (includes psycopg2 for PostgreSQL) |
| `database.py` | Reads DATABASE_URL from environment |
| `.env.example` | Template for environment variables |
| `main.py` | FastAPI app entry point |
| `frontend/` | HTML/CSS/JS served as static files |

---

## Architecture on Vercel

```
┌─────────────────┐
│  Your Browser   │
└────────┬────────┘
         │
    ┌────▼────────────────────────┐
    │  Vercel (Edge Network)       │
    │                              │
    │  ┌──────────────────────┐    │
    │  │ FastAPI Backend      │    │
    │  │ - Auth endpoints     │    │
    │  │ - Report API         │    │
    │  │ - Notifications      │    │
    │  └─────────┬────────────┘    │
    │            │                 │
    └────────────┼─────────────────┘
                 │
    ┌────────────▼─────────────────┐
    │  PostgreSQL Database         │
    │  (Neon/Supabase/Railway)     │
    │                              │
    │  - Users                     │
    │  - Reports                   │
    │  - Sessions                  │
    └──────────────────────────────┘
```

---

## Monitoring & Maintenance

### View Logs
- Vercel Dashboard → Deployments → Click latest → Logs

### Monitor Database
- Neon Dashboard → Monitoring tab
- Supabase Dashboard → Database section

### Update Code
```bash
# Make changes locally
# Test with: python -m uvicorn main:app --reload

git add .
git commit -m "Feature: description"
git push origin main

# Vercel auto-deploys! Watch in dashboard
```

---

## Costs

| Service | Free Tier | Cost |
|---------|-----------|------|
| Vercel | ✅ Yes | $0/month |
| Neon | ✅ Yes | $0/month (small projects) |
| Supabase | ✅ Yes | $0/month (small projects) |
| Gmail SMTP | ✅ Yes | $0/month |
| **Total** | | **$0/month** |

---

## Troubleshooting

### Issue: "Build failed"
**Solution**: Check build logs in Vercel dashboard. Common issues:
- Missing `requirements.txt`
- Python syntax error
- Missing environment variable

### Issue: "Database connection error"
**Solution**: 
- Verify DATABASE_URL is correct
- Test connection locally first
- Ensure database accepts remote connections

### Issue: "Reports not showing"
**Solution**:
- Check DATABASE_URL is set
- Database might need initialization
- Check logs for SQL errors

### Issue: "Email not working"
**Solution**:
- If using Gmail, generate app-specific password
- Verify SMTP credentials in environment variables
- Try `EMAIL_BACKEND=console` to debug

---

## Security Best Practices

✅ **Do:**
- Keep `.env` file locally only
- Use environment variables on Vercel
- Generate app-specific passwords (not main password)
- Use HTTPS (automatic on Vercel)
- Keep dependencies updated

❌ **Don't:**
- Commit `.env` file to GitHub
- Use main Gmail password
- Share ADMIN_EMAIL credentials
- Disable CORS without reason
- Use SQLite on Vercel (ephemeral filesystem)

---

## Advanced: Custom Domain

After initial deployment:

1. Buy domain (Namecheap, GoDaddy, Google Domains)
2. In Vercel: Settings → Domains
3. Add your domain
4. Follow DNS setup instructions
5. SSL certificate auto-generated
6. ✅ Your app at `https://yourdomain.com`

---

## What's Next?

After successful deployment:

1. **Invite Users** - Share deployment URL
2. **Monitor Usage** - Check Vercel logs regularly
3. **Enhance Features** - Add more reports, analytics
4. **Scale Database** - Upgrade if needed
5. **Custom Domain** - Point your domain name

---

## Support & Resources

- **Vercel Docs**: https://vercel.com/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **SQLAlchemy Docs**: https://docs.sqlalchemy.org
- **Neon Docs**: https://neon.tech/docs
- **Supabase Docs**: https://supabase.com/docs

---

## Quick Reference Commands

```bash
# Test locally
python -m uvicorn main:app --reload

# Push to GitHub
git add . && git commit -m "message" && git push origin main

# Test deployment
python test_deployment.py

# View environment variables
vercel env ls

# Pull env vars locally
vercel env pull .env.local
```

---

**You're ready to deploy! 🚀**

Follow the **30-Minute Deployment** section above and your app will be live!

Any questions? Check DEPLOYMENT.md, GITHUB_VERCEL_SETUP.md, or VERCEL_CHECKLIST.md
