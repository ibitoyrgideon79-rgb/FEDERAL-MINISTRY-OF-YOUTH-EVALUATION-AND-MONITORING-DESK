# 🎯 Vercel Deployment - Quick Reference Card

## Print This & Keep Handy!

---

## 📱 3-Step Deployment

### 1️⃣ GITHUB (5 min)
```bash
cd DMT
git init
git add .
git commit -m "Initial"
git remote add origin https://github.com/YOU/dmt.git
git push -u origin main
```

### 2️⃣ DATABASE (5 min)
- Go to https://neon.tech
- Sign up with GitHub
- Create project
- Copy: `postgresql://user:pass@host/dmt`

### 3️⃣ VERCEL (10 min)
- Go to https://vercel.com
- Import GitHub repo
- Add 9 environment variables (see below)
- Click Deploy ✅

---

## 🔐 Environment Variables

| Variable | Example | Priority |
|----------|---------|----------|
| `DATABASE_URL` | `postgresql://...` | 🔴 CRITICAL |
| `ADMIN_EMAIL` | `admin@gmail.com` | 🔴 CRITICAL |
| `EMAIL_BACKEND` | `console` | 🟡 Important |
| `SMTP_HOST` | `smtp.gmail.com` | 🟡 Important |
| `SMTP_PORT` | `587` | 🟡 Important |
| `SMTP_USERNAME` | `admin@gmail.com` | 🟡 Important |
| `SMTP_PASSWORD` | (16-char app pwd) | 🟡 Important |
| `FROM_EMAIL` | `admin@gmail.com` | 🟡 Important |
| `SESSION_EXPIRE_DAYS` | `30` | 🟢 Optional |

---

## ⚡ Critical URLs

| Service | URL |
|---------|-----|
| **GitHub** | https://github.com/new |
| **Neon** | https://neon.tech |
| **Supabase** | https://supabase.com |
| **Vercel** | https://vercel.com |
| **Gmail App Pwd** | https://myaccount.google.com/apppasswords |

---

## 🆘 Common Issues

| Error | Fix |
|-------|-----|
| Build failed | ✅ Check `requirements.txt` exists |
| Database error | ✅ Verify DATABASE_URL is correct |
| Email not sending | ✅ Check SMTP password (app-specific) |
| Reports not showing | ✅ Test database connection |
| 404 on pages | ✅ Frontend files in `/frontend` folder |

---

## 📋 Testing After Deploy

```bash
# Test API
python test_deployment.py

# In browser:
- Login: https://your-domain.vercel.app
- Dashboard: https://your-domain.vercel.app/dashboard.html
- Analytics: https://your-domain.vercel.app/analytics.html

# Test submission:
1. Login with email
2. Enter OTP
3. Go to dashboard
4. Click "Submit Report" on a programme
5. Fill form & submit
6. Check admin email for notification
```

---

## 🔑 Gmail Setup for SMTP

1. Enable 2FA on Gmail
2. Go to: https://myaccount.google.com/apppasswords
3. Select: Mail + Windows Computer
4. Copy 16-character password
5. Use as `SMTP_PASSWORD` in Vercel
6. Use your email as `SMTP_USERNAME`

---

## 📊 Documentation Files

| File | Read When |
|------|-----------|
| `VERCEL_QUICK_START.md` | First thing - full guide |
| `GITHUB_VERCEL_SETUP.md` | Need detailed steps |
| `DEPLOYMENT.md` | Full documentation |
| `ARCHITECTURE.md` | Want to understand system |
| `VERCEL_CHECKLIST.md` | Before/after deployment |
| `test_deployment.py` | Testing after deploy |

---

## ✅ Deployment Checklist

- [ ] GitHub account created
- [ ] Code pushed to GitHub
- [ ] PostgreSQL database created (Neon)
- [ ] Connection string copied
- [ ] Vercel account created
- [ ] Repository imported into Vercel
- [ ] 9 environment variables added
- [ ] Deployment successful (no red errors)
- [ ] App loads in browser
- [ ] Can login with email
- [ ] Can submit report
- [ ] Admin receives email

---

## 🚀 Commands Cheatsheet

```bash
# Git
git init                              # Initialize repo
git add .                            # Stage files
git commit -m "message"              # Commit
git push origin main                 # Push to GitHub

# Local testing
python -m uvicorn main:app --reload  # Run locally

# Deployment verification
python test_deployment.py             # Test API

# Vercel CLI
vercel login                         # Login to Vercel
vercel                               # Deploy from CLI
vercel logs --tail                   # View logs
vercel env ls                        # List env vars
vercel env pull                      # Pull env locally
```

---

## 💰 Cost Summary

| Service | Cost |
|---------|------|
| **Total Monthly** | **$0** ✅ |
| Vercel | Free |
| PostgreSQL | Free |
| Email | Free |
| Domain | Optional (~$12/year) |

---

## 🎯 Deployment Timeline

| Step | Time | What Happens |
|------|------|--------------|
| Push code | 30s | GitHub updated |
| Trigger Vercel | 5s | Webhook triggered |
| Build Python | 60s | Dependencies installed |
| Run server | 10s | FastAPI starts |
| Initialize DB | 30s | Tables created |
| Deploy complete | - | App is LIVE ✅ |
| **Total** | **~2 min** | |

---

## 📞 Support

- **Vercel Issues**: https://vercel.com/help
- **Database Issues**: https://neon.tech/docs
- **FastAPI Help**: https://fastapi.tiangolo.com/help
- **GitHub Help**: https://docs.github.com

---

## ⚠️ DO's and DON'Ts

### ✅ DO
- Use environment variables for secrets
- Keep `.env` file locally only
- Use app-specific Gmail password
- Enable 2FA on accounts
- Push frequently to GitHub
- Monitor Vercel logs

### ❌ DON'T
- Commit `.env` to GitHub
- Use SQLite on Vercel
- Share credentials in code
- Use main Gmail password
- Disable CORS without reason
- Ignore deployment warnings

---

## 🎓 Prerequisites

✅ Basic command line knowledge
✅ GitHub account (free)
✅ Vercel account (free)
✅ Email account (for notifications)
✅ 30 minutes of time

---

## 🏁 When Deployment is Done

✅ Your app is LIVE at: `https://your-domain.vercel.app`
✅ Users can login with OTP
✅ Reports stored in PostgreSQL
✅ Analytics working with charts
✅ Admin receives notifications
✅ Everything auto-scales with Vercel

**Now what?**
- Share URL with team
- Monitor logs in Vercel dashboard
- Update code by pushing to GitHub
- Vercel auto-deploys on push!

---

## 🚀 Ready to Deploy?

**Next Step**: Open and read `VERCEL_QUICK_START.md`

**Estimated Time**: 30 minutes total

**Result**: Live production application! 🎉

---

*Last Updated: February 5, 2026*
*DMT v1.0 - Vercel Edition*

**Questions?** Check DEPLOYMENT.md for comprehensive guide.
