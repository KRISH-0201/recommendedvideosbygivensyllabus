from flask import Flask, render_template, request, flash
from googleapiclient.discovery import build
from rake_nltk import Rake
import nltk
from isodate import parse_duration
from datetime import datetime, timezone
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file
import os

app = Flask(__name__)
app.secret_key = "krish_secret_key"

nltk.download('punkt')
nltk.download('stopwords')

API_KEY = os.environ.get('YOUTUBE_API_KEY')
if not API_KEY: # This checks if API_KEY is None (i.e., not found)
    raise ValueError("YOUTUBE_API_KEY environment variable not set. Please set it before running the app.")

youtube = build('youtube', 'v3', developerKey=API_KEY)

TRUSTED_CHANNELS = {'Khan Academy', 'Unacademy', 'nptelhrd', 'Physics Wallah', 'edureka!'}

def extract_keyphrases(text):
    rake = Rake()
    rake.extract_keywords_from_text(text)
    phrases = [p.strip() for p in rake.get_ranked_phrases() if len(p.strip()) > 3][:8]
    if not phrases:
        from nltk.tokenize import sent_tokenize
        phrases = [t.strip() for t in sent_tokenize(text) if len(t.strip()) > 5]
    return phrases

def score_video(video, topic, trusted_only=False):
    engagement = (video['likes'] / video['views']) if video['views'] else 0
    try:
        dt = datetime.strptime(video.get('publishedAt','')[:10], "%Y-%m-%d")
        recency = 1 if (datetime.now(timezone.utc) - dt).days < 720 else 0
    except: recency = 0
    keyword_match = 1 if topic.lower() in video['title'].lower() else 0
    channel_bonus = 1 if trusted_only and video.get('channelTitle','') in TRUSTED_CHANNELS else 0
    return (2*engagement) + (0.8*recency) + (0.5*keyword_match) + channel_bonus + (video['views'] / 5e5)

def search_youtube(topic, prefs):
    try:
        video_duration = prefs.get('duration')
        published_after = prefs.get('recent')
        trusted_only = prefs.get('trusted_only', False)
        min_views = prefs.get('min_views', 3000)
        min_likes = prefs.get('min_likes', 20)
        max_count = prefs.get('max_results', 7)

        search_args = dict(q=topic, part='id,snippet', type='video', maxResults=max_count)
        if published_after:
            search_args['publishedAfter'] = published_after
        videos = []
        response = youtube.search().list(**search_args).execute()
        video_ids = [item['id']['videoId'] for item in response.get('items', [])]
        if not video_ids:
            return []
        resp = youtube.videos().list(part='statistics,contentDetails,snippet', id=','.join(video_ids)).execute()
        for video in resp.get('items', []):
            stats, snippet, details = video.get('statistics', {}), video.get('snippet', {}), video.get('contentDetails', {})
            try: duration_sec = parse_duration(details.get('duration', 'PT0S')).total_seconds()
            except: duration_sec = 0
            if video_duration == 'short' and duration_sec > 900: continue
            if video_duration == 'long' and duration_sec < 1500: continue
            title = snippet.get('title','')
            channel = snippet.get('channelTitle','')
            publishedAt = snippet.get('publishedAt','')
            views = int(stats.get('viewCount',0))
            likes = int(stats.get('likeCount',0)) if 'likeCount' in stats else 0
            if views < min_views or likes < min_likes: continue
            if trusted_only and channel not in TRUSTED_CHANNELS: continue
            videos.append({
                'videoId': video['id'], 'title': title, 'channelTitle': channel,
                'views': views, 'likes': likes, 'duration': duration_sec,
                'publishedAt': publishedAt, 'topic': topic,
                'thumbnail': snippet.get('thumbnails', {}).get('medium', {}).get('url'),
                'url': f'https://youtube.com/watch?v={video["id"]}',
                'trusted': channel in TRUSTED_CHANNELS
            })
        videos = sorted(videos, key=lambda v: score_video(v, topic, trusted_only), reverse=True)
        return videos[:prefs.get('topn',3)]
    except Exception as e:
        print('API error:', e)
        return "error"

@app.route("/", methods=['GET','POST'])
def index():
    videos_by_topic = []
    preferences = {
        'duration': request.form.get('duration', 'any'),
        'recent': ("2022-01-01T00:00:00Z" if request.form.get('recent') == 'yes' else None),
        'trusted_only': request.form.get('trusted_only') == "on",
        'min_views': 3000, 'min_likes': 20,
        'max_results': 7, 'topn': 3
    }
    if request.method == 'POST':
        syllabus = request.form.get('syllabus','').strip()
        if not syllabus or len(syllabus) < 5:
            flash("Please enter your syllabus for smart recommendations.", "warning")
            return render_template('index.html', videos_by_topic=[], userprefs=preferences)
        keyphrases = extract_keyphrases(syllabus)
        found_any = False
        for topic in keyphrases:
            result = search_youtube(topic, preferences)
            if result == "error":
                flash('Something went wrong with YouTube Search.',"danger")
                break
            if result:
                found_any = True
                videos_by_topic.append({'topic': topic, 'videos': result})
        if not found_any:
            flash('No relevant videos found for your topics/filters. Try again!', 'danger')
        else:
            flash(f"Found {sum(len(t['videos']) for t in videos_by_topic)} relevant videos.", "success")
    return render_template('index.html', videos_by_topic=videos_by_topic, userprefs=preferences)

if __name__=="__main__":
    app.run(debug=True) 
