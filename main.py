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

# ================= IMAGE =================
def get_image(query):
    try:
        url = f"https://api.unsplash.com/photos/random?query={query}&client_id={UNSPLASH_KEY}"
        return requests.get(url).json()["urls"]["regular"]
    except:
        return None

def get_context_image(text):
    text = text.lower()

    if "sad" in text:
        return get_image("sad emotional person")
    elif "happy" in text:
        return get_image("happy success moment")
    elif "fear" in text or "dark" in text:
        return get_image("dark horror scene")
    elif "journey" in text:
        return get_image("travel journey road")
    elif "ai" in text:
        return get_image("futuristic ai technology")

    return get_image(text[:40])

# ================= CLEAN =================
def clean_text(text):
    text = text.replace("**", "")
    text = text.replace("Honestly,", "")
    return text

# ================= GENERATE =================
def generate(topic, mode):

    if mode == "morning":
        topic = ", ".join(get_news()[:5])
        prompt = f"Write a detailed blog on: {topic}"

    elif mode == "night":
        topic = random.choice(get_trending())
        prompt = f"Write a detailed blog on: {topic}"

    elif mode == "evening":
        prompt = "Write about trending AI tools"

    else:
        prompt = f"Write a human-like story about {topic}"

    prompt += """
- No markdown (**)
- No robotic tone
- Use headings naturally
- Make content long and engaging
"""

    res = client.chat.completions.create(
        model="meta/llama-3.1-70b-instruct",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9,
        max_tokens=1500
    )

    return res.choices[0].message.content, topic

# ================= FORMAT =================
def format_blog(content, keyword):

    lines = content.split("\n")

    raw_title = lines[0].strip()

    # 🔥 SEO TITLE (NO HTML)
    title = raw_title + " 🔥"

    # Styled title inside content
    styled_title = f"<h1 style='font-weight:bold;color:#111'>{raw_title}</h1>"

    body = styled_title

    for line in lines[1:]:

        line = line.strip()
        if not line:
            continue

        # Headings
        if len(line) < 80 and line.istitle():
            body += f"<h2 style='font-weight:bold;color:#222;margin-top:20px'>{line}</h2>"

        else:
            if "happy" in line.lower():
                line += " 😊"
            elif "sad" in line.lower():
                line += " 😔"
            elif "fear" in line.lower():
                line += " 😨"

            body += f"<p style='line-height:1.8'>{line}</p>"

            # Context image
            if random.random() > 0.6:
                img = get_context_image(line)
                if img:
                    body += f'<img src="{img}" style="width:100%;margin:15px 0;border-radius:10px;">'

    # Top image
    top_img = get_image(keyword)
    if top_img:
        body = f'<img src="{top_img}" style="width:100%;border-radius:10px;"><br><br>' + body

    return title, body

# ================= PUBLISH =================
def publish(title, content):
    service = build("blogger", "v3", credentials=authenticate())

    service.posts().insert(
        blogId=get_blog_id(),
        body={
            "title": title,  # ✅ FIXED
            "content": content,
            "labels": ["Blog", "SEO", "Trending"]
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
    content = clean_text(content)

    title, body = format_blog(content, keyword)
    publish(title, body)

if __name__ == "__main__":
    run()
