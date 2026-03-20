# 🎓 StudyFind — Syllabus-Based YouTube Video Recommender

**🌟 Live Demo:** [https://recommendedvideosbygivensyllabus.onrender.com](https://recommendedvideosbygivensyllabus.onrender.com/)

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

Open your browser at `http://localhost:8080`

> **No `.env` file needed!** This app uses an internal Python `httpx` web scraper which works without any API key.

---

## ☁️ Deploy to Render (Free)

1. Push your project to GitHub
2. Go to [render.com](https://render.com) → **New** → **Web Service**
3. Connect your GitHub repo
4. Render will ask for some deployment settings. Ensure you have:
   - **Start Command:** `gunicorn app:app`
   - **Environment Variable:** `PYTHON_VERSION` set to `3.11.0` (or newer)
5. Click **Deploy** and your app is live! 🎉



## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python + Flask |
| NLP | RAKE-NLTK |
| YouTube Search | `httpx` raw scraper (no API key!) |
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
- All searches happen server-side via `httpx` scraping.

---

Feel free to contribute or report issues! ⭐ Star the repo if you find it helpful.
