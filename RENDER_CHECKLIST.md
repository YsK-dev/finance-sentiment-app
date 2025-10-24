# 🚀 Render Deployment Checklist

Use this checklist to ensure smooth deployment to Render.com

## ☑️ Pre-Deployment Checklist

### 1. Code Preparation
- [ ] All code committed to Git
- [ ] `.env` files are in `.gitignore` (never commit secrets!)
- [ ] `requirements.txt` is up to date (no conda packages)
- [ ] Frontend uses environment variable for API URL (`VITE_API_URL`)
- [ ] All tests passing locally

### 2. MongoDB Atlas Setup
- [ ] Created MongoDB Atlas account
- [ ] Created free M0 cluster
- [ ] Created database user with password
- [ ] Whitelisted IP `0.0.0.0/0` (allow all)
- [ ] Copied connection string
- [ ] Tested connection locally

### 3. GitHub Repository
- [ ] Created GitHub repository (must be **Public** for free tier)
- [ ] Pushed all code to GitHub
- [ ] Repository includes `render.yaml` (optional but recommended)

## 🔧 Deployment Steps

### Backend Deployment
- [ ] Created Render account
- [ ] Connected GitHub repository
- [ ] Created Web Service (Python)
- [ ] Set Root Directory: `backend`
- [ ] Set Build Command: `pip install -r requirements.txt`
- [ ] Set Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- [ ] Added `MONGODB_URI` environment variable
- [ ] Added `DB_NAME` environment variable
- [ ] Deployment successful (waited 5-10 minutes)
- [ ] Backend URL copied: `https://________________.onrender.com`

### Frontend Deployment
- [ ] Created Static Site on Render
- [ ] Set Root Directory: `frontend`
- [ ] Set Build Command: `npm install && npm run build`
- [ ] Set Publish Directory: `dist`
- [ ] Added `VITE_API_URL` environment variable (backend URL)
- [ ] Deployment successful (2-3 minutes)
- [ ] Frontend URL copied: `https://________________.onrender.com`

## ✅ Post-Deployment Testing

### Test Backend
- [ ] Visit: `https://your-backend.onrender.com` (should see "Finance Sentiment API")
- [ ] Visit: `https://your-backend.onrender.com/docs` (API documentation loads)
- [ ] Test health endpoint: `https://your-backend.onrender.com/health`

### Test Frontend
- [ ] Visit: `https://your-frontend.onrender.com`
- [ ] App loads without errors
- [ ] Can enter stock symbol
- [ ] Click "Analyze" works (may take 30-60s first time)
- [ ] Results display correctly
- [ ] Can view news articles
- [ ] YouTube analyzer works

### Database Connection
- [ ] Backend connects to MongoDB (check Render logs)
- [ ] Analysis results are saved
- [ ] No connection errors in logs

## 🐛 Troubleshooting

### Build Fails
- [ ] Check Render build logs for errors
- [ ] Verify `requirements.txt` has no conda packages (no `@` symbols)
- [ ] Check Node version matches (18+)
- [ ] Verify all dependencies are listed

### Connection Errors
- [ ] Verify `VITE_API_URL` points to backend (with `https://`)
- [ ] Check CORS settings in backend `main.py`
- [ ] Verify MongoDB connection string is correct
- [ ] Check MongoDB Atlas IP whitelist includes `0.0.0.0/0`

### Cold Start Issues
- [ ] First request takes 30-60 seconds (normal for free tier)
- [ ] Set up UptimeRobot to keep backend warm
- [ ] Consider upgrading to paid plan ($7/month) for instant response

## 🎯 Optional Enhancements

### Keep Backend Warm
- [ ] Sign up for [UptimeRobot](https://uptimerobot.com/) (free)
- [ ] Add HTTP monitor: `https://your-backend.onrender.com/health`
- [ ] Set interval: 5 minutes
- [ ] Backend stays warm (no cold starts)

### Custom Domain
- [ ] Purchase domain name
- [ ] Add custom domain in Render settings
- [ ] Update DNS records
- [ ] Enable SSL/TLS (automatic on Render)

### Environment Variables
- [ ] Add `NEWS_API_KEY` (optional - 100 requests/day free)
- [ ] Add `FINNHUB_API_KEY` (optional - 60 calls/min free)
- [ ] Restart services after adding keys

## 📊 Monitoring

### Check Service Health
- [ ] Backend service shows "Live" status
- [ ] Frontend service shows "Live" status
- [ ] No error spikes in metrics

### Review Logs
- [ ] Backend logs show successful startup
- [ ] FinBERT model loads correctly
- [ ] MongoDB connection successful
- [ ] No repeated errors

### Performance Metrics
- [ ] Response times acceptable
- [ ] Build times under 10 minutes
- [ ] Deploy times under 5 minutes

## 🎉 Success Criteria

Your deployment is successful when:

✅ Backend URL returns API documentation  
✅ Frontend loads and displays correctly  
✅ Can analyze stock symbols  
✅ Results show sentiment and recommendations  
✅ News articles display  
✅ YouTube analyzer works  
✅ No console errors  
✅ MongoDB stores results  

## 📝 Notes

**Free Tier Limitations:**
- Backend spins down after 15 minutes of inactivity
- Cold start takes 30-60 seconds
- 750 hours/month shared across all free services
- No credit card required!

**Upgrade Benefits ($7/month per service):**
- No cold starts (always on)
- Faster response times
- More memory and CPU
- Priority support

## 🔗 Important Links

- [ ] Backend URL: `https://__________________.onrender.com`
- [ ] Frontend URL: `https://__________________.onrender.com`
- [ ] MongoDB Atlas: `https://cloud.mongodb.com`
- [ ] Render Dashboard: `https://dashboard.render.com`
- [ ] GitHub Repo: `https://github.com/___________/___________`

## 📚 Documentation

- [DEPLOY_TO_RENDER.md](DEPLOY_TO_RENDER.md) - Detailed deployment guide
- [Render Docs](https://render.com/docs) - Official Render documentation
- [MongoDB Atlas Docs](https://docs.atlas.mongodb.com/) - MongoDB documentation

---

**Deployment Date**: _______________  
**Deployed By**: _______________  
**Status**: ⬜ In Progress | ⬜ Completed | ⬜ Failed  

**Happy Deploying! 🚀**
