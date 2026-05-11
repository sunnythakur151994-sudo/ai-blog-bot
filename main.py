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

# ================= HUMAN STYLE =================
def humanize(text):
    starters = ["Honestly,", "I think", "To be real,", "In my opinion,"]
    parts = text.split(". ")

    for i in range(0, len(parts), 3):
        parts[i] = random.choice(starters) + " " + parts[i]

    return ". ".join(parts)

def add_story(text):
    return random.choice([
        "I remember when I first saw something like this...",
        "Not gonna lie, this surprised me...",
        "This reminded me of something I experienced..."
    ]) + "<br><br>" + text

# ================= GENERATOR =================
def generate(topic, mode):

    styles = [
        "engaging storytelling",
        "professional blog",
        "casual friendly tone",
        "high energy viral style"
    ]

    style = random.choice(styles)

    if mode == "morning":
        topic = ", ".join(get_news()[:5])
        prompt = f"""
Write a visually attractive blog using:

{topic}

- Use emojis
- Bold headings
- Each news should have explanation
- Add opinion
"""

    elif mode == "night":
        topic = random.choice(get_trending())
        prompt = f"""
Write a viral trending blog on:

{topic}

- Why trending
- Full explanation
- Opinion
"""

    elif mode == "evening":
        prompt = "Write about trending AI tools with visuals and excitement"

    else:
        prompt = f"Write a story about {topic} with emotional storytelling"

    prompt += f"""

STYLE:
- {style}
- Add emojis (not too many)
- Use bold headings
- Break into sections
- Make it engaging and readable
"""

    res = client.chat.completions.create(
        model="meta/llama-3.1-70b-instruct",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9,
        max_tokens=1200
    )

    return res.choices[0].message.content, topic

# ================= FORMAT =================
def format_blog(content, keyword):

    sections = content.split("\n")
    title = sections[0].replace("#", "").strip() + " 🔥"

    body = ""

    for sec in sections[1:]:
        if len(sec.strip()) < 5:
            continue

        # Add bold headings
        if sec.lower().startswith("##") or sec.isupper():
            body += f"<h2><b>{sec}</b></h2>"

        else:
            body += f"<p>{sec}</p>"

            # Add image after some paragraphs
            if random.random() > 0.6:
                img = get_image(keyword)
                if img:
                    body += f'<img src="{img}" style="width:100%;margin:10px 0;border-radius:10px;">'

    # Add top image
    top_img = get_image(keyword)
    if top_img:
        body = f'<img src="{top_img}" style="width:100%;border-radius:12px;"><br><br>' + body

    # Monetization
    body += """
    <br><br>
    👉 <b>Recommended:</b> https://amzn.to/YOUR-LINK  
    👉 <b>More guides:</b> Visit our blog daily!
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
            "labels": ["Trending", "AI", "News"]
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
    content = add_story(content)

    title, body = format_blog(content, keyword)
    publish(title, body)

if __name__ == "__main__":
    run()
