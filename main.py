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

client = OpenAI(
    api_key=NVIDIA_API_KEY,
    base_url="https://integrate.api.nvidia.com/v1"
)

# ================= AUTH =================
def authenticate():
    creds_dict = json.loads(GOOGLE_TOKEN)
    return Credentials.from_authorized_user_info(creds_dict)

def get_blog_id():
    return random.choice(BLOG_IDS)

# ================= DATA =================
def get_news():
    try:
        url = f"https://newsapi.org/v2/top-headlines?country=in&pageSize=10&apiKey={NEWS_API_KEY}"
        res = requests.get(url).json()
        return [a["title"] for a in res.get("articles", []) if a.get("title")]
    except:
        return ["latest news"]

def get_trending():
    try:
        url = "https://trends.google.com/trending/rss?geo=IN"
        root = ET.fromstring(requests.get(url).content)
        return [item.text for item in root.findall(".//item/title")]
    except:
        return ["trending topic"]

def get_image(query):
    try:
        url = f"https://api.unsplash.com/photos/random?query={query}&client_id={UNSPLASH_KEY}"
        return requests.get(url).json()["urls"]["regular"]
    except:
        return None

# ================= HUMANIZER =================
def humanize(text):
    # remove AI-like phrases
    text = text.replace("Honestly,", "")
    text = text.replace("In conclusion,", "")
    text = text.replace("Overall,", "")

    return text

# ================= GENERATOR =================
def generate(topic, mode):

    if mode == "morning":
        topic = ", ".join(get_news()[:5])
        prompt = f"""
Write a clean, professional blog using these real news headlines:

{topic}

Instructions:
- Do NOT use stars (**)
- Do NOT use markdown
- Use natural human tone
- Write like a real blogger
- No emojis
- No repeated phrases
- Use proper headings (like section titles)
"""

    elif mode == "night":
        topic = random.choice(get_trending())
        prompt = f"""
Write a blog on this trending topic:

{topic}

Explain it naturally like a human writer.
No markdown or symbols.
"""

    elif mode == "evening":
        prompt = """
Write about trending AI tools in a clean blog style.
"""

    else:
        prompt = f"""
Write a real-life style story about {topic}

Make it emotional and natural.
Avoid robotic tone.
"""

    res = client.chat.completions.create(
        model="meta/llama-3.1-70b-instruct",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.85,
        max_tokens=1200
    )

    return res.choices[0].message.content, topic

# ================= FORMAT =================
def format_blog(content, keyword):

    lines = content.split("\n")

    title = lines[0].strip()
    body = ""

    for line in lines[1:]:

        line = line.strip()

        if not line:
            continue

        # Detect headings (clean)
        if len(line) < 80 and line.istitle():
            body += f"<h2 style='font-weight:bold;margin-top:20px'>{line}</h2>"
        else:
            body += f"<p style='line-height:1.7'>{line}</p>"

            # Insert images naturally
            if random.random() > 0.7:
                img = get_image(keyword)
                if img:
                    body += f'<img src="{img}" style="width:100%;margin:15px 0;border-radius:8px;">'

    # Top image
    top_img = get_image(keyword)
    if top_img:
        body = f'<img src="{top_img}" style="width:100%;border-radius:10px;"><br><br>' + body

    # Monetization placeholder
    body += """
    <br><br>
    <b>Recommended:</b> https://amzn.to/YOUR-LINK
    """

    return title, body

# ================= PUBLISH =================
def publish(title, content):
    service = build("blogger", "v3", credentials=authenticate())

    service.posts().insert(
        blogId=get_blog_id(),
        body={
            "title": title,
            "content": content,
            "labels": ["Blog", "News", "AI"]
        }
    ).execute()

    print("✅ Posted:", title)

# ================= MAIN =================
def run():
    hour = datetime.utcnow().hour

    if 3 <= hour < 7:
        mode = "morning"
        topic = "latest news"

    elif 7 <= hour < 12:
        mode = "afternoon"
        topic = "life story"

    elif 12 <= hour < 17:
        mode = "evening"
        topic = "AI tools"

    else:
        mode = "night"
        topic = "trending"

    content, keyword = generate(topic, mode)
    content = humanize(content)

    title, body = format_blog(content, keyword)
    publish(title, body)

if __name__ == "__main__":
    run()
