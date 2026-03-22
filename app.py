from flask import Flask, render_template, request, flash  # type: ignore[import-untyped]
from rake_nltk import Rake  # type: ignore[import-untyped]
import nltk  # type: ignore[import-untyped]
import httpx
import json
import re
import os

from itertools import islice

# ---------------------------------------------------------------------------
# NLTK setup – download required data quietly
# ---------------------------------------------------------------------------
for _pkg in ("punkt", "punkt_tab", "stopwords"):
    try:
        nltk.download(_pkg, quiet=True)
    except Exception:
        pass

app = Flask(__name__)
app.secret_key = "krish_secret_key_2025"

TRUSTED_CHANNELS = {
    "Khan Academy",
    "Unacademy",
    "nptelhrd",
    "Physics Wallah - Alakh Pandey",
    "Physics Wallah",
    "edureka!",
    "MIT OpenCourseWare",
    "freeCodeCamp.org",
    "Simplilearn",
    "3Blue1Brown",
    "Corey Schafer",
    "Sentdex",
    "TED-Ed",
    "CrashCourse",
    "Vsauce",
    "Numberphile",
    "Computerphile",
    "StatQuest with Josh Starmer",
    "Two Minute Papers",
    "Andrej Karpathy",
}

# ---------------------------------------------------------------------------
# NLP helpers
# ---------------------------------------------------------------------------

def extract_keyphrases(text: str) -> list:
    """Extract top key phrases from syllabus text using RAKE."""
    rake = Rake()
    rake.extract_keywords_from_text(text)
    phrases = [p.strip() for p in rake.get_ranked_phrases() if len(p.strip()) > 3]
    phrases = list(islice(phrases, 10))
    if not phrases:
        # Fallback: split by comma / newline
        phrases = [t.strip() for t in text.replace(",", "\n").splitlines() if len(t.strip()) > 3]
    return list(islice(phrases, 8))


# ---------------------------------------------------------------------------
# YouTube search via httpx (no API key required)
# ---------------------------------------------------------------------------

_YT_SEARCH_URL = "https://www.youtube.com/results"
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def _extract_yt_initial_data(html: str) -> dict:
    """Pull ytInitialData JSON out of raw YouTube HTML."""
    match = re.search(r"var ytInitialData\s*=\s*(\{.+?\});\s*</script>", html, re.DOTALL)
    if not match:
        # Fallback pattern
        match = re.search(r"ytInitialData\s*=\s*(\{.+?\});", html, re.DOTALL)
    if not match:
        return {}
    try:
        return json.loads(match.group(1))  # type: ignore[no-any-return]
    except Exception:
        return {}


def _parse_view_count(text: str) -> int:
    """Convert '1.2M views' or '1,234,567 views' to int."""
    text = text.lower().replace(",", "").replace("views", "").strip()
    try:
        if "b" in text:
            return int(float(text.replace("b", "").strip()) * 1_000_000_000)
        if "m" in text:
            return int(float(text.replace("m", "").strip()) * 1_000_000)
        if "k" in text:
            return int(float(text.replace("k", "").strip()) * 1_000)
        digits = "".join(c for c in text if c.isdigit())
        return int(digits) if digits else 0
    except Exception:
        return 0


def _format_count(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


def _duration_to_sec(s: str) -> int:
    """'1:02:34' or '10:30' -> seconds."""
    try:
        parts = [int(p) for p in s.split(":")]
        if len(parts) == 3:
            return parts[0] * 3600 + parts[1] * 60 + parts[2]
        if len(parts) == 2:
            return parts[0] * 60 + parts[1]
        return parts[0]
    except Exception:
        return 0


def _score(video: dict, topic: str) -> float:
    views = video.get("views_raw", 0)
    keyword_match = 1.0 if topic.lower() in video.get("title", "").lower() else 0.0
    channel_bonus = 1.5 if video.get("trusted") else 0.0
    view_score = views / 500_000
    return (0.5 * keyword_match) + channel_bonus + view_score


def _fetch_videos(query: str, limit: int = 15) -> list:
    """Fetch YouTube search results using httpx and parse ytInitialData."""
    try:
        with httpx.Client(headers=_HEADERS, timeout=15, follow_redirects=True) as client:
            resp = client.get(_YT_SEARCH_URL, params={"search_query": query, "sp": "EgIQAQ%3D%3D"})
            resp.raise_for_status()
            html = resp.text
    except Exception as e:
        print(f"[YouTube fetch error] {e}")
        return []

    data = _extract_yt_initial_data(html)
    if not data:
        return []

    try:
        contents = (
            data["contents"]["twoColumnSearchResultsRenderer"]
            ["primaryContents"]["sectionListRenderer"]
            ["contents"][0]["itemSectionRenderer"]["contents"]
        )
    except (KeyError, IndexError, TypeError):
        return []

    videos = []
    for item in contents:
        vr = item.get("videoRenderer")
        if not vr:
            continue
        try:
            video_id = vr.get("videoId", "")
            title_runs = vr.get("title", {}).get("runs", [])
            title = title_runs[0].get("text", "") if title_runs else ""
            channel = vr.get("ownerText", {}).get("runs", [{}])[0].get("text", "")
            duration_str = vr.get("lengthText", {}).get("simpleText", "0:00")
            view_text = vr.get("viewCountText", {}).get("simpleText", "0")
            thumbnails = vr.get("thumbnail", {}).get("thumbnails", [])
            thumbnail = thumbnails[-1].get("url", "") if thumbnails else ""
            published = vr.get("publishedTimeText", {}).get("simpleText", "")

            if not video_id or not title:
                continue

            views_raw = _parse_view_count(view_text)
            duration_sec = _duration_to_sec(duration_str)
            trusted = channel in TRUSTED_CHANNELS

            videos.append(
                {
                    "videoId": video_id,
                    "title": title,
                    "channelTitle": channel,
                    "views_raw": views_raw,
                    "views": _format_count(views_raw),
                    "duration": duration_str,
                    "duration_sec": duration_sec,
                    "publishedAt": published,
                    "thumbnail": thumbnail,
                    "url": f"https://youtube.com/watch?v={video_id}",
                    "trusted": trusted,
                }
            )
            if len(videos) >= limit:
                break
        except Exception:
            continue

    return videos


def search_youtube(topic: str, prefs: dict) -> list:
    """Search YouTube and return filtered + ranked results."""
    video_duration_pref = prefs.get("duration", "any")
    trusted_only = prefs.get("trusted_only", False)
    min_views = int(prefs.get("min_views", 1000))
    topn = int(prefs.get("topn", 3))

    videos = _fetch_videos(topic, limit=20)

    filtered = []
    for v in videos:
        dur = v.get("duration_sec", 0)
        if video_duration_pref == "short" and dur > 900:
            continue
        if video_duration_pref == "long" and dur < 1500:
            continue
        if v.get("views_raw", 0) < min_views:
            continue
        if trusted_only and not v.get("trusted"):
            continue
        filtered.append(v)

    filtered.sort(key=lambda v: _score(v, topic), reverse=True)
    return list(islice(filtered, topn))


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/", methods=["GET", "POST"])
def index():
    videos_by_topic: list = []
    preferences = {
        "duration": request.form.get("duration", "any"),
        "trusted_only": request.form.get("trusted_only") == "on",
        "min_views": 1000,
        "topn": 3,
    }

    if request.method == "POST":
        syllabus = request.form.get("syllabus", "").strip()
        if not syllabus or len(syllabus) < 3:
            flash("Please enter your syllabus or topic for smart recommendations.", "warning")
            return render_template("index.html", videos_by_topic=[], userprefs=preferences)

        keyphrases = extract_keyphrases(syllabus)
        if not keyphrases:
            flash("Could not extract topics. Try listing topics separated by commas.", "warning")
            return render_template("index.html", videos_by_topic=[], userprefs=preferences)

        for topic in keyphrases:
            result = search_youtube(topic, preferences)
            if result:
                videos_by_topic.append({"topic": topic, "videos": result})

        if not videos_by_topic:
            flash("No relevant videos found. Try relaxing filters or using different text!", "warning")
        else:
            total = sum(len(t["videos"]) for t in videos_by_topic)
            topics_count = len(videos_by_topic)
            flash(
                f"Found {total} video{'s' if total != 1 else ''} "
                f"across {topics_count} topic{'s' if topics_count != 1 else ''}!",
                "success",
            )

    return render_template("index.html", videos_by_topic=videos_by_topic, userprefs=preferences)


if __name__ == "__main__":
    import os

    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
