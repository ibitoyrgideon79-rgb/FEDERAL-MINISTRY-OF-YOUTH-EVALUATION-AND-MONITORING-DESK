# Quick GitHub & Vercel Setup

## 1. Initialize Git Repository (if not already done)

```bash
cd c:\Users\user\Desktop\DMT

# Initialize git
git init

# Add all files
git add .

# Create first commit
git commit -m "Initial DMT deployment setup"

# Rename branch to main
git branch -M main
```

## 2. Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `dmt` (or your preferred name)
3. Description: "Digital Monitoring Tool - FastAPI Backend with Analytics"
4. Choose **Public** (for free tier) or **Private** (if you have GitHub Pro)
5. Click "Create repository"

## 3. Connect Local Repository to GitHub

```bash
# Add remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/dmt.git

# Push code to GitHub
git push -u origin main
```

## 4. Deploy to Vercel

### Option A: Using Vercel Dashboard (Easiest)

1. Go to https://vercel.com
2. Sign up with GitHub
3. Click "New Project"
4. Select "Import Git Repository"
5. Find and select your `dmt` repository
6. Click "Import"
7. Framework Preset: Select "Other" (Python auto-detected)
8. **Configure Environment Variables** (very important!):
   - Click "Environment Variables"
   - Add each variable:
     ```
     DATABASE_URL = postgresql://user:password@host:port/dmt
     ADMIN_EMAIL = admin@example.com
     EMAIL_BACKEND = console
     SMTP_HOST = smtp.gmail.com
     SMTP_PORT = 587
     SMTP_USERNAME = your_email@gmail.com
     SMTP_PASSWORD = app_specific_password
     FROM_EMAIL = your_email@gmail.com
     SESSION_EXPIRE_DAYS = 30
     ```
9. Click "Deploy"
10. Wait for deployment to complete (~2-5 minutes)

### Option B: Using Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy from DMT directory
cd c:\Users\user\Desktop\DMT
vercel

# Follow prompts and set environment variables
```

## 5. After Deployment

Your app will be available at:
- `https://dmt.vercel.app` (or custom domain)

Test it:
1. Open in browser
2. Login with test email
3. Submit a report
4. Check admin email for notification
5. View analytics

## Environment Variables Explained

| Variable | Example | Purpose |
|----------|---------|---------|
| `DATABASE_URL` | `postgresql://...` | Connection to PostgreSQL (Neon/Supabase/Railway) |
| `ADMIN_EMAIL` | `admin@gmail.com` | Email that gets admin privileges |
| `EMAIL_BACKEND` | `console` or `smtp` | How to send emails |
| `SMTP_HOST` | `smtp.gmail.com` | Email server hostname |
| `SMTP_PORT` | `587` | Email server port |
| `SMTP_USERNAME` | `your_email@gmail.com` | Email username |
| `SMTP_PASSWORD` | (16-char app password) | Email password |
| `FROM_EMAIL` | `noreply@gmail.com` | Sender email address |
| `SESSION_EXPIRE_DAYS` | `30` | How long sessions last |

## Database Setup Before Deployment

### Using Neon (Free Tier)

1. Go to https://neon.tech
2. Sign up with GitHub
3. Create new project
4. Get connection string (looks like):
   ```
   postgresql://neondb_owner:abc123@ep-xxxxx.neon.tech/neondb?sslmode=require
   ```
5. Copy this and paste as `DATABASE_URL` in Vercel

### Using Supabase (Free Tier)

1. Go to https://supabase.com
2. Sign up with GitHub
3. Create new project (choose region nearest you)
4. Go to Settings → Database → Connection Pooling
5. Get connection string
6. Replace `[YOUR-PASSWORD]` with your password
7. Copy and paste as `DATABASE_URL` in Vercel

## Email Setup with Gmail

1. Enable 2-Factor Authentication on Gmail
2. Go to https://myaccount.google.com/apppasswords
3. Select "Mail" and "Windows Computer"
4. Google generates 16-character password
5. Use as `SMTP_PASSWORD` in Vercel

## Troubleshooting

### Deployment Failed
- Check build logs in Vercel dashboard
- Ensure `requirements.txt` has all dependencies
- Verify `main.py` exists and is runnable

### Database Connection Error
- Test connection string locally first
- Ensure DATABASE_URL is set correctly
- Check database is publicly accessible

### Reports Not Saving
- Verify DATABASE_URL is correct
- Check database tables exist
- Manually initialize database if needed

### Email Not Sending
- Verify SMTP credentials are correct
- Check Gmail app password (not main password)
- Try `EMAIL_BACKEND=console` first to debug

## Next Steps

- ✅ Code pushed to GitHub
- ✅ App deployed to Vercel
- ✅ Database connected
- ✅ Email configured
- ⏭️ Share URL with team
- ⏭️ Start using the app!

## Useful Commands

```bash
# View deployment logs
vercel logs --tail

# Check environment variables (view only)
vercel env ls

# Redeploy latest commit
vercel --prod

# Open Vercel dashboard for project
vercel open

# Pull environment variables to local
vercel env pull .env.local
```

---

**Deployment Complete!** 🚀

Your app is now live at your Vercel URL. Users can:
- Login with OTP
- Submit reports
- View analytics
- Admins get email notifications
