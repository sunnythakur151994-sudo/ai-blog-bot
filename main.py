import os
import json
import requests
from datetime import datetime
from openai import OpenAI  # we will point this to NVIDIA endpoint
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# =========================
# 🔐 CONFIG
# =========================

BLOG_ID = "8997390388821877620"  # 👈 put your blog ID here

NVIDIA_API_KEY = os.environ.get("NVIDIA_API_KEY")
UNSPLASH_KEY = os.environ.get("UNSPLASH_KEY")
GOOGLE_TOKEN = os.environ.get("GOOGLE_TOKEN")

# =========================
# 🤖 NVIDIA CLIENT
# =========================

client = OpenAI(
    api_key=NVIDIA_API_KEY,
    base_url="https://integrate.api.nvidia.com/v1"
)

# =========================
# 🔐 GOOGLE AUTH
# =========================

def authenticate():
    creds_dict = json.loads(GOOGLE_TOKEN)
    return Credentials.from_authorized_user_info(creds_dict)

# =========================
# 🖼️ GET IMAGE
# =========================

def get_image(query):
    try:
        url = f"https://api.unsplash.com/photos/random?query={query}&client_id={UNSPLASH_KEY}"
        res = requests.get(url).json()
        return res["urls"]["regular"]
    except:
        return None

# =========================
# ✍️ GENERATE BLOG (MODES)
# =========================

def generate_blog(topic, mode):
    if mode == "morning":
        prompt = f"""
Write a SEO optimized blog on today's top 10 news.

Include:
- Top 10 current affairs
- Explain each in detail
- Add your opinion on each
- Human tone (not robotic)
"""

    elif mode == "afternoon":
        prompt = f"""
Write an engaging story about: {topic}

- Personal storytelling style
- Feels like real human experience
- Emotional and engaging
"""

    elif mode == "evening":
        prompt = f"""
Write about trending AI tools and tech trends.

- Latest tools
- Use cases
- Your opinion
- SEO optimized
"""

    else:
        prompt = f"""
Write a trending SEO blog on: {topic}
"""

    response = client.chat.completions.create(
        model="meta/llama-3.1-70b-instruct",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=1200
    )

    return response.choices[0].message.content

# =========================
# 🧹 FORMAT BLOG
# =========================

def format_blog(content, topic):
    lines = content.split("\n")

    title = lines[0].replace("#", "").strip()
    body = "<br>".join(lines[1:])

    image_url = get_image(topic)

    if image_url:
        img = f'<img src="{image_url}" style="width:100%; margin-bottom:20px;">'
        body = img + body

    return title, body

# =========================
# 🌐 PUBLISH
# =========================

def publish_post(title, content):
    creds = authenticate()
    service = build("blogger", "v3", credentials=creds)

    post = {
        "title": title,
        "content": content,
        "labels": ["AI", "Tech", "Trending"]
    }

    service.posts().insert(blogId=BLOG_ID, body=post).execute()
    print(f"✅ Posted: {title}")

# =========================
# 🔁 MAIN BOT
# =========================

def run_bot():
    hour = datetime.utcnow().hour

    if 3 <= hour < 7:
        mode = "morning"
        topic = "today world news India"

    elif 7 <= hour < 12:
        mode = "afternoon"
        topic = "adventure life story"

    elif 12 <= hour < 17:
        mode = "evening"
        topic = "latest AI tools 2026"

    else:
        mode = "night"
        topic = "trending global topics"

    print(f"Running mode: {mode}")

    content = generate_blog(topic, mode)
    title, body = format_blog(content, topic)

    publish_post(title, body)

# =========================

if __name__ == "__main__":
    run_bot()
