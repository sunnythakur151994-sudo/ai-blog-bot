import os
import json
import random
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from openai import OpenAI
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# ================= CONFIG =================
BLOG_IDS = ["8997390388821877620"]

NVIDIA_API_KEY = os.environ.get("NVIDIA_API_KEY")
GOOGLE_TOKEN = os.environ.get("GOOGLE_TOKEN")
UNSPLASH_KEY = os.environ.get("UNSPLASH_KEY")
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")

MEDIUM_TOKEN = os.environ.get("MEDIUM_TOKEN")
DEVTO_API_KEY = os.environ.get("DEVTO_API_KEY")

client = OpenAI(
    api_key=NVIDIA_API_KEY,
    base_url="https://integrate.api.nvidia.com/v1"
)

# ================= AUTH =================
def authenticate():
    creds_dict = json.loads(GOOGLE_TOKEN)
    return Credentials.from_authorized_user_info(creds_dict)

# ================= DATA =================
def get_news():
    try:
        url = f"https://newsapi.org/v2/top-headlines?country=in&pageSize=10&apiKey={NEWS_API_KEY}"
        res = requests.get(url).json()
        return [a["title"] for a in res.get("articles", []) if a.get("title")]
    except:
        return ["latest news"]

# ================= GENERATE =================
def generate():
    topic = ", ".join(get_news()[:3])

    prompt = f"""
Write a clean, human-like blog on:

{topic}

No markdown, no stars.
Use headings and natural tone.
"""

    res = client.chat.completions.create(
        model="meta/llama-3.1-70b-instruct",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9,
        max_tokens=1200
    )

    return res.choices[0].message.content

# ================= BLOGGER =================
def post_blogger(title, content):
    service = build("blogger", "v3", credentials=authenticate())

    service.posts().insert(
        blogId=random.choice(BLOG_IDS),
        body={"title": title, "content": content}
    ).execute()

    print("✅ Blogger Posted")

# ================= MEDIUM =================
def post_medium(title, content):
    try:
        headers = {
            "Authorization": f"Bearer {MEDIUM_TOKEN}",
            "Content-Type": "application/json"
        }

        data = {
            "title": title,
            "contentFormat": "html",
            "content": content,
            "publishStatus": "public"
        }

        # You must replace USER_ID manually
        requests.post(
            "https://api.medium.com/v1/users/YOUR_USER_ID/posts",
            headers=headers,
            json=data
        )

        print("✅ Medium Posted")
    except:
        print("❌ Medium Failed")

# ================= DEVTO =================
def post_devto(title, content):
    try:
        headers = {
            "api-key": DEVTO_API_KEY,
            "Content-Type": "application/json"
        }

        data = {
            "article": {
                "title": title,
                "published": True,
                "body_markdown": content
            }
        }

        requests.post(
            "https://dev.to/api/articles",
            headers=headers,
            json=data
        )

        print("✅ Dev.to Posted")
    except:
        print("❌ Dev.to Failed")

# ================= LINKEDIN (SIMPLIFIED) =================
def post_linkedin(title):
    print("⚠ LinkedIn requires manual or advanced API setup")

# ================= MAIN =================
def run():
    content = generate()
    lines = content.split("\n")

    title = lines[0].strip()
    body = "<br>".join(lines[1:])

    # Post everywhere
    post_blogger(title, body)
    post_medium(title, body)
    post_devto(title, content)
    post_linkedin(title)

if __name__ == "__main__":
    run()
