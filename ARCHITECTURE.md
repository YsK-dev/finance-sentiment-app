# 🏗️ Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        USER'S BROWSER                         │
│                   (Anywhere in the world)                     │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ HTTPS
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              🌐 RENDER FRONTEND (Free Tier)                  │
│                                                               │
│  - Static React App                                          │
│  - Vite Build (dist/)                                        │
│  - Served via CDN                                            │
│  - URL: https://finance-sentiment-frontend.onrender.com      │
│  - Cost: $0/month                                            │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ API Calls
                        │ HTTPS
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              🐍 RENDER BACKEND (Free Tier)                   │
│                                                               │
│  - Python 3.11 + FastAPI                                     │
│  - Uvicorn Server                                            │
│  - FinBERT AI Model                                          │
│  - URL: https://finance-sentiment-backend.onrender.com       │
│  - Cost: $0/month                                            │
│  - Cold Start: 30-60s after 15 min idle                      │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ MongoDB
                        │ Connection
                        │ (TLS/SSL)
                        ▼
┌─────────────────────────────────────────────────────────────┐
│            🗄️  MONGODB ATLAS (Free Tier M0)                 │
│                                                               │
│  - 512 MB Storage                                            │
│  - Shared CPU                                                │
│  - Database: finance_sentiment                               │
│  - Region: AWS (your choice)                                 │
│  - Cost: $0/month                                            │
└─────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────┐
│                    EXTERNAL DATA SOURCES                      │
│                                                               │
│  📰 Yahoo Finance RSS  → Free                                │
│  📰 Google News        → Free                                │
│  📰 NewsAPI (optional) → 100 req/day free                    │
│  📊 Finnhub (optional) → 60 calls/min free                   │
│  🎥 YouTube Transcripts → Free                               │
└─────────────────────────────────────────────────────────────┘
```

## 🔄 Data Flow

```
1. User enters stock symbol (e.g., "AAPL")
   ↓
2. Frontend sends request to Backend API
   ↓
3. Backend collects data from multiple sources:
   - Yahoo Finance RSS feeds
   - Google News articles
   - (Optional) NewsAPI
   - (Optional) Finnhub
   ↓
4. Backend analyzes sentiment using FinBERT AI
   ↓
5. Backend stores results in MongoDB
   ↓
6. Backend returns analysis to Frontend
   ↓
7. Frontend displays:
   - Sentiment scores
   - Investment advice
   - Risk factors
   - Source articles
```

## 📊 Request Flow Example

```
┌────────┐
│ User   │ Enters "TSLA"
└───┬────┘
    │
    ▼
┌────────────────┐
│ Frontend       │ GET /api/analysis/symbol/TSLA
└───┬────────────┘
    │
    ▼
┌────────────────┐
│ Backend API    │ 1. Collect data from 5+ sources
│                │ 2. Analyze with FinBERT
│                │ 3. Generate recommendations
└───┬────────────┘
    │
    ├──────────┐
    │          │
    ▼          ▼
┌─────────┐  ┌──────────┐
│ MongoDB │  │ External │
│ Store   │  │ APIs     │
└────┬────┘  └────┬─────┘
     │            │
     └──────┬─────┘
            │
            ▼
┌────────────────────┐
│ Results Returned   │
│ - Sentiment: 78%   │
│ - Action: BUY      │
│ - Risk: Medium     │
└────────────────────┘
```

## 🌍 Geographic Distribution

```
        ┌─────────────────────────────────────┐
        │    Render Edge Network (CDN)        │
        │  Frontend cached at edge locations  │
        └─────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
   ┌────────┐      ┌────────┐      ┌────────┐
   │ US West│      │ US East│      │ Europe │
   └────────┘      └────────┘      └────────┘
        │                │                │
        └────────────────┼────────────────┘
                         │
                         ▼
              ┌──────────────────┐
              │  Backend Server  │
              │  (Single Region) │
              └──────────────────┘
                         │
                         ▼
              ┌──────────────────┐
              │  MongoDB Cluster │
              │  (AWS Region)    │
              └──────────────────┘
```

## 🔒 Security Architecture

```
┌──────────────────────────────────────────┐
│            Security Layers                │
└──────────────────────────────────────────┘

1. ┌─────────────────────────────┐
   │ HTTPS/TLS (Automatic)       │
   │ - SSL certificates          │
   │ - Secure connections        │
   └─────────────────────────────┘

2. ┌─────────────────────────────┐
   │ CORS Protection             │
   │ - Allowed origins only      │
   │ - Request validation        │
   └─────────────────────────────┘

3. ┌─────────────────────────────┐
   │ MongoDB Security            │
   │ - User authentication       │
   │ - IP whitelist              │
   │ - Encrypted connections     │
   └─────────────────────────────┘

4. ┌─────────────────────────────┐
   │ Environment Variables       │
   │ - Secrets not in code       │
   │ - Render secrets manager    │
   └─────────────────────────────┘

5. ┌─────────────────────────────┐
   │ Rate Limiting               │
   │ - asyncio-throttle          │
   │ - Prevents abuse            │
   └─────────────────────────────┘
```

## 💰 Cost Breakdown (Monthly)

```
┌─────────────────────────────────────────────────┐
│ Service              │ Tier      │ Cost         │
├─────────────────────────────────────────────────┤
│ Render Frontend      │ Free      │ $0.00        │
│ Render Backend       │ Free      │ $0.00        │
│ MongoDB Atlas        │ M0 Free   │ $0.00        │
│ NewsAPI              │ 100/day   │ $0.00        │
│ Finnhub              │ 60/min    │ $0.00        │
│ UptimeRobot          │ 50 checks │ $0.00        │
├─────────────────────────────────────────────────┤
│ TOTAL                │           │ $0.00/month  │
└─────────────────────────────────────────────────┘

Optional Upgrades:
┌─────────────────────────────────────────────────┐
│ Render Backend       │ Starter   │ $7.00/month  │
│ Render Frontend      │ Starter   │ $7.00/month  │
│ MongoDB Atlas        │ M10       │ $57.00/month │
└─────────────────────────────────────────────────┘
```

## 🚀 Performance Characteristics

```
Free Tier:
├─ Frontend
│  ├─ Load Time: <1s (CDN cached)
│  ├─ First Paint: <2s
│  └─ Interactive: <3s
│
└─ Backend
   ├─ Warm Request: 200-500ms
   ├─ Cold Start: 30-60s (after 15 min idle)
   └─ Sleep After: 15 minutes

With UptimeRobot (pings every 5 min):
└─ Backend
   ├─ Never sleeps
   └─ Always warm: 200-500ms
```

## 📈 Scalability

```
Current (Free Tier):
├─ Concurrent Users: ~100
├─ Requests/min: ~60
└─ Storage: 512 MB

Starter Tier ($7/month):
├─ Concurrent Users: ~500
├─ Requests/min: ~200
└─ Storage: Same (512 MB)

Professional ($25/month):
├─ Concurrent Users: ~2000
├─ Requests/min: ~1000
└─ Storage: Upgrade to M10 ($57/mo)
```

## 🔄 Deployment Pipeline

```
┌──────────────┐
│ Local Dev    │ Code changes
└──────┬───────┘
       │
       │ git push
       ▼
┌──────────────┐
│ GitHub       │ Version control
└──────┬───────┘
       │
       │ Webhook
       ▼
┌──────────────┐
│ Render       │ Auto-detect changes
└──────┬───────┘
       │
       ├─────────────┬────────────┐
       │             │            │
       ▼             ▼            ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│ Build    │  │ Test     │  │ Deploy   │
│ 5-10 min │  │ Auto     │  │ 1-2 min  │
└──────────┘  └──────────┘  └──────────┘
       │             │            │
       └─────────────┴────────────┘
                     │
                     ▼
              ┌──────────┐
              │ Live! 🚀 │
              └──────────┘
```

## 🎯 Architecture Benefits

✅ **Zero Cost** - Completely free (with cold starts)
✅ **Global CDN** - Fast frontend delivery
✅ **Auto-scaling** - Render handles traffic spikes
✅ **HTTPS** - Secure by default
✅ **Auto-deploys** - Push to GitHub → Live
✅ **Monitoring** - Built-in metrics and logs
✅ **Backups** - MongoDB automated backups
✅ **High Availability** - 99.9% uptime SLA

## 🛠️ Technology Stack

```
Frontend:
├─ React 18
├─ Vite 4.5
├─ TailwindCSS 3
├─ Axios
└─ React Router 6

Backend:
├─ Python 3.11
├─ FastAPI 0.104
├─ Uvicorn
├─ Transformers (FinBERT)
├─ PyTorch
└─ Motor (Async MongoDB)

Database:
└─ MongoDB 6.0

Infrastructure:
├─ Render.com
├─ MongoDB Atlas
└─ GitHub
```

---

**Architecture Version**: 1.0  
**Last Updated**: October 2025  
**Total Monthly Cost**: $0 🎉
