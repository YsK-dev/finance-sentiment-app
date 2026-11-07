# 🚀 Deploy to Render.com - Step by Step Guide

This guide will help you deploy your Finance Sentiment Analysis app to Render.com **for FREE**.

## 📋 Prerequisites

1. **GitHub Account** - [Sign up](https://github.com/signup) if you don't have one
2. **Render Account** - [Sign up](https://render.com/signup) (free, no credit card required)
3. **MongoDB Atlas Account** - [Sign up](https://www.mongodb.com/cloud/atlas/register) (free tier available)

---

## 🗄️ Step 1: Set Up MongoDB Atlas (Free Database)

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Click **"Try Free"** or **"Sign In"**
3. Create a new **Free Cluster** (M0 Sandbox):
   - Choose **AWS** as provider
   - Select a region close to you
   - Click **"Create Cluster"**

4. **Create Database User**:
   - Go to **Database Access** in left sidebar
   - Click **"Add New Database User"**
   - Choose **Password** authentication
   - Username: `finance_app`
   - Password: Generate a strong password (save it!)
   - User Privileges: **Read and write to any database**
   - Click **"Add User"**

5. **Whitelist IP Addresses**:
   - Go to **Network Access** in left sidebar
   - Click **"Add IP Address"**
   - Click **"Allow Access from Anywhere"** (for Render)
   - Confirm with **"0.0.0.0/0"**
   - Click **"Confirm"**

6. **Get Connection String**:
   - Go to **Database** → **Connect**
   - Choose **"Connect your application"**
   - Copy the connection string (looks like):
   ```
   mongodb+srv://finance_app:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
   - Replace `<password>` with your actual password
   - **Save this connection string** - you'll need it!

---

## 📦 Step 2: Push Code to GitHub

1. **Initialize Git** (if not already done):
   ```bash
   cd /Users/ysk/Downloads/birikim-main-main/birikim/finance-sentiment-app
   git init
   git add .
   git commit -m "Initial commit - ready for Render deployment"
   ```

2. **Create GitHub Repository**:
   - Go to [GitHub](https://github.com/new)
   - Repository name: `finance-sentiment-app`
   - Make it **Public** (required for Render free tier)
   - Click **"Create repository"**

3. **Push to GitHub**:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/finance-sentiment-app.git
   git branch -M main
   git push -u origin main
   ```

---

## 🖥️ Step 3: Deploy Backend to Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**

3. **Connect GitHub Repository**:
   - Click **"Connect GitHub"**
   - Select your repository: `finance-sentiment-app`
   - Click **"Connect"**

4. **Configure Backend Service**:
   ```
   Name: finance-sentiment-backend
   Region: Choose closest to you
   Branch: main
   Root Directory: backend
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   Instance Type: Free
   ```

5. **Add Environment Variables**:
   Click **"Advanced"** → **"Add Environment Variable"**
   
   Add these variables:
   ```
   MONGODB_URI = mongodb+srv://finance_app:YOUR_PASSWORD@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   DB_NAME = finance_sentiment
   PYTHON_VERSION = 3.11.0
   ```
   
   ⚠️ **Replace with your actual MongoDB connection string!**

6. Click **"Create Web Service"**

7. **Wait for deployment** (5-10 minutes for first deployment due to ML model downloads)
   - You'll see build logs in real-time
   - When done, you'll see: ✅ **"Live"**
   - Copy your backend URL: `https://finance-sentiment-backend.onrender.com`

---

## 🌐 Step 4: Deploy Frontend to Render

1. Click **"New +"** → **"Static Site"**

2. **Connect Same Repository**:
   - Select your repository: `finance-sentiment-app`

3. **Configure Frontend Service**:
   ```
   Name: finance-sentiment-frontend
   Branch: main
   Root Directory: frontend
   Build Command: npm install && npm run build
   Publish Directory: dist
   ```

4. **Add Environment Variable**:
   ```
   VITE_API_URL = https://finance-sentiment-backend.onrender.com
   ```
   ⚠️ **Use YOUR backend URL from Step 3!**

5. Click **"Create Static Site"**

6. **Wait for deployment** (2-3 minutes)
   - When done: ✅ **"Live"**
   - Your app URL: `https://finance-sentiment-frontend.onrender.com`

---

## ✅ Step 5: Test Your Deployment

1. Open your frontend URL: `https://finance-sentiment-frontend.onrender.com`
2. Try analyzing a stock symbol (e.g., **AAPL**, **TSLA**)
3. First request might take 30-60 seconds (cold start)
4. Subsequent requests will be faster!

---

## 🔧 Alternative: One-Click Deployment with Blueprint

Render also supports deploying everything at once using `render.yaml`:

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Blueprint"**
3. Connect your GitHub repository
4. Render will detect `render.yaml` and configure everything automatically!
5. Add your **MONGODB_URI** in the environment variables section
6. Click **"Apply"**

---

## 🎯 Important Notes

### Free Tier Limitations:
- ⏱️ **Backend spins down after 15 minutes of inactivity**
- ⏳ **Cold start takes 30-60 seconds** (first request after sleep)
- 💾 **750 hours/month free** (enough for one service 24/7)
- 🚀 **Use multiple services = share the 750 hours**

### Keeping Backend Awake (Optional):
If you want to prevent cold starts, use a free service like:
- [UptimeRobot](https://uptimerobot.com/) - Ping your backend every 5 minutes
- [Cron-job.org](https://cron-job.org/) - Schedule health checks

### Cost Estimate:
- ✅ **MongoDB Atlas**: FREE (M0 tier - 512MB storage)
- ✅ **Render Backend**: FREE (with cold starts)
- ✅ **Render Frontend**: FREE
- 💰 **Total**: $0/month

### To Upgrade (Remove Cold Starts):
- Upgrade Render backend to **Starter ($7/month)** - stays always on
- Still cheaper than most alternatives!

---

## 🐛 Troubleshooting

### Backend Build Fails:
- Check if `requirements.txt` has only standard pip packages (no conda)
- Increase instance size if memory issues occur

### Frontend Can't Connect to Backend:
- Verify `VITE_API_URL` environment variable is set correctly
- Check backend URL includes `https://` (not `http://`)
- Ensure MongoDB connection string is correct

### Database Connection Errors:
- Verify MongoDB Atlas allows connections from `0.0.0.0/0`
- Check if password in connection string is URL-encoded
- Test connection string locally first

### Cold Start Issues:
- First request after 15 min takes 30-60 seconds (normal for free tier)
- Set up UptimeRobot to ping every 5 minutes (keeps it warm)

---

## 🎉 Success!

Your app is now live and accessible worldwide! Share your URL with others:

🌐 **Frontend**: `https://finance-sentiment-frontend.onrender.com`
🔧 **Backend API**: `https://finance-sentiment-backend.onrender.com`

---

## 📚 Additional Resources

- [Render Docs](https://render.com/docs)
- [MongoDB Atlas Docs](https://docs.atlas.mongodb.com/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Vite Build Guide](https://vitejs.dev/guide/build.html)

---

**Need Help?** Check Render logs:
- Dashboard → Your Service → **Logs** tab
- Real-time logs help debug issues

**Happy Deploying! 🚀**
