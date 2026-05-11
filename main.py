import os
import json
import random
import requests
import time
from datetime import datetime
from openai import OpenAI
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# ================= CONFIG =================
BLOG_ID = "8997390388821877620"

NVIDIA_API_KEY = os.environ.get("NVIDIA_API_KEY")
GOOGLE_TOKEN = os.environ.get("GOOGLE_TOKEN")
UNSPLASH_KEY = os.environ.get("UNSPLASH_KEY")
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")
DEVTO_API_KEY = os.environ.get("DEVTO_API_KEY")

client = OpenAI(
    api_key=NVIDIA_API_KEY,
    base_url="https://integrate.api.nvidia.com/v1"
)

# ================= AUTH =================
def authenticate():
    creds_dict = json.loads(GOOGLE_TOKEN)
    return Credentials.from_authorized_user_info(creds_dict)

# ================= TREND =================
def get_topic():
    try:
        url = f"https://newsapi.org/v2/top-headlines?country=in&pageSize=5&apiKey={NEWS_API_KEY}"
        res = requests.get(url).json()
        titles = [a["title"] for a in res.get("articles", []) if a.get("title")]
        return ", ".join(titles)
    except:
        return "latest trending topic"

# ================= IMAGE =================
def get_image(query):
    try:
        url = f"https://api.unsplash.com/photos/random?query={query}&client_id={UNSPLASH_KEY}"
        return requests.get(url).json()["urls"]["regular"]
    except:
        return None

# ================= BLOGGER CONTENT =================
def generate_blogger(topic):

    prompt = f"""
Write a HIGH QUALITY SEO blog.

Act like top 50 ranking blogs.

Rules:
- First line = powerful headline
- Use headings
- Long detailed content
- Human tone
- No markdown

Topic:
{topic}
"""

    res = client.chat.completions.create(
        model="meta/llama-3.1-70b-instruct",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9,
        max_tokens=1600
    )

    return res.choices[0].message.content

# ================= DEVTO CONTENT =================
def generate_devto(topic):

    prompt = f"""
Write a DEV.TO style article.

Rules:
- Technical + informative
- Shorter than blog
- Direct tone
- Developer friendly

Topic:
{topic}
"""

    res = client.chat.completions.create(
        model="meta/llama-3.1-70b-instruct",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
        max_tokens=900
    )

    return res.choices[0].message.content

# ================= FORMAT =================
def format_blog(content):

    lines = content.split("\n")
    title = next((l.strip() for l in lines if l.strip()), "Latest Update") + " 🔥"

    html = f"<h1 style='font-weight:bold'>{title}</h1>"

    count = 0

    for line in lines[1:]:

        line = line.strip()
        if not line:
            continue

        if len(line) < 80 and line[0].isupper():
            html += f"<h2 style='font-weight:bold'>{line}</h2>"
        else:
            html += f"<p>{line}</p>"
            count += 1

            if count % 2 == 0:
                img = get_image(line[:30])
                if img:
                    html += f'<img src="{img}" style="width:100%;margin:10px 0;">'

    return title, html

# ================= BLOGGER =================
def post_blogger(title, content):
    service = build("blogger", "v3", credentials=authenticate())

    service.posts().insert(
        blogId=BLOG_ID,
        body={"title": title, "content": content}
    ).execute()

    print("✅ Blogger posted")

# ================= DEVTO =================
def post_devto(title, content):

    if not DEVTO_API_KEY:
        print("Dev key missing")
        return

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

    r = requests.post("https://dev.to/api/articles", headers=headers, json=data)

    print("Dev.to:", r.status_code)

# ================= MAIN =================
def run():

    hour = datetime.utcnow().hour

    topic = get_topic()

    print("Generating Blogger content...")
    blog_content = generate_blogger(topic)

    print("Formatting...")
    title, html = format_blog(blog_content)

    print("Posting Blogger...")
    post_blogger(title, html)

    # ================= DEV TIMING CONTROL =================
    # Delay to simulate evening peak
    print("Waiting before Dev.to post...")
    time.sleep(20)  # small delay (GitHub safe)

    print("Generating Dev.to content...")
    dev_content = generate_devto(topic)

    print("Posting Dev.to...")
    post_devto(title, dev_content)

if __name__ == "__main__":
    run()
