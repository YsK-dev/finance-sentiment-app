# 🚀 DEPLOY NOW - Quick Start

**Time Required**: 20-25 minutes  
**Cost**: $0/month (FREE!)  
**Difficulty**: Easy ⭐⭐☆☆☆

---

## 📋 What You Need

- [ ] GitHub account ([Sign up](https://github.com/signup))
- [ ] Render account ([Sign up](https://render.com/signup))
- [ ] MongoDB Atlas account ([Sign up](https://www.mongodb.com/cloud/atlas/register))

*All accounts are FREE - no credit card required!*

---

## ⚡ Quick Deploy (3 Steps)

### Step 1: Get MongoDB Connection String (5 min)

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas/register)
2. Create free cluster (M0 Sandbox)
3. Create database user (save password!)
4. Whitelist IP: `0.0.0.0/0`
5. Get connection string:
   ```
   mongodb+srv://username:password@cluster.mongodb.net/
   ```

### Step 2: Push to GitHub (2 min)

```bash
cd /Users/ysk/Downloads/birikim-main-main/birikim/finance-sentiment-app
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/finance-sentiment-app.git
git push -u origin main
```

### Step 3: Deploy on Render (15 min)

**Backend:**
1. Go to [Render Dashboard](https://dashboard.render.com/)
2. New → Web Service
3. Connect GitHub repo
4. Configure:
   - Name: `finance-sentiment-backend`
   - Root Directory: `backend`
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Add env var: `MONGODB_URI` = your connection string
5. Create Web Service (wait 5-10 min)
6. Copy backend URL

**Frontend:**
1. New → Static Site
2. Same repo
3. Configure:
   - Name: `finance-sentiment-frontend`
   - Root Directory: `frontend`
   - Build: `npm install && npm run build`
   - Publish: `dist`
   - Add env var: `VITE_API_URL` = your backend URL (include https://)
4. Create Static Site (wait 2-3 min)

---

## ✅ Done!

Visit your frontend URL and test with "AAPL" or "TSLA"!

---

## 📚 Need More Help?

- **Detailed Guide**: [DEPLOY_TO_RENDER.md](DEPLOY_TO_RENDER.md)
- **Checklist**: [RENDER_CHECKLIST.md](RENDER_CHECKLIST.md)
- **Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)

---

## 🐛 Quick Fixes

**Backend won't start?**
- Check Render logs
- Verify `MONGODB_URI` is correct
- Wait for model to download (first time: 5-10 min)

**Frontend can't connect?**
- Check `VITE_API_URL` has `https://` prefix
- Verify backend is "Live" in Render
- Test backend URL directly in browser

**Database connection failed?**
- Check MongoDB Atlas IP whitelist (`0.0.0.0/0`)
- Verify database user credentials
- Test connection string locally

---

## 🎯 Success Checklist

- [ ] Backend shows "Live" ✅
- [ ] Frontend shows "Live" ✅
- [ ] Can analyze stock symbols ✅
- [ ] Results display correctly ✅
- [ ] No console errors ✅

---

**Your app is LIVE! 🎉**

Share it: `https://your-app.onrender.com`
