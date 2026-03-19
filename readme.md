# 🎓 StudyFind — Syllabus-Based YouTube Video Recommender

Paste any syllabus, topic list, or subject name — the app automatically extracts key topics and finds the most relevant YouTube educational videos for each one. **No API key required!**

## ✨ Features

- 🔍 **Intelligent Topic Extraction** — uses RAKE NLP to extract key phrases from your syllabus
- 📺 **YouTube Search** — finds top videos for each topic (no API key needed!)
- ⭐ **Smart Ranking** — scores videos by views, recency, keyword match, and trusted channels
- ✅ **Trusted Channel Badge** — highlights Khan Academy, freeCodeCamp, edureka!, MIT OCW, etc.
- 🎨 **Beautiful UI** — glassmorphism design with dark mode, animations, and responsive layout
- ⏱️ **Duration Filter** — filter short (<15 min) or long (>25 min) videos
- 📅 **Recency Filter** — only show videos from the last 2 years

## 🚀 Local Setup

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/recommendedvideosbygivensyllabus.git
cd recommendedvideosbygivensyllabus
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the app
```bash
python app.py
```

Open your browser at `http://localhost:5000`

> **No `.env` file needed!** This app uses `youtube-search-python` which works without any API key.

---

## ☁️ Deploy to Render (Free)

1. Push your project to GitHub
2. Go to [render.com](https://render.com) → **New** → **Web Service**
3. Connect your GitHub repo
4. Render auto-detects `render.yaml` — click **Deploy**
5. Your app is live! 🎉

## ☁️ Deploy to Railway (Alternative)

1. Push your project to GitHub  
2. Go to [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub Repo**
3. Railway auto-detects `Procfile` and deploys using gunicorn
4. Your app is live in ~2 minutes!

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python + Flask |
| NLP | RAKE-NLTK |
| YouTube Search | youtube-search-python (no API key!) |
| Frontend | Bootstrap 5 + Vanilla CSS + Animate.css |
| Production Server | Gunicorn |
| Deployment | Render / Railway |

## 📁 Project Structure

```
recommendedvideosbygivensyllabus/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── Procfile            # Gunicorn start command (for Heroku/Railway/Render)
├── render.yaml         # Render.com deployment config
├── .env.example        # Environment variables template
├── .gitignore          
├── templates/
│   └── index.html      # Main UI page
└── static/
    ├── styles.css       # Custom styling
    ├── main.js          # Blob animation + card fade-in
    └── krish_logo.png   # Logo image
```

## 🔒 Security

- No API keys are stored or required
- No user data is collected or stored
- All searches happen server-side via `youtube-search-python`

---

Feel free to contribute or report issues! ⭐ Star the repo if you find it helpful.
