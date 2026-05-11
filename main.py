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

# 🔥 MULTI BLOG SUPPORT (ADD MORE IDS HERE)
BLOG_IDS = [
    "8997390388821877620",
    # "SECOND_BLOG_ID",
]

NVIDIA_API_KEY = os.environ.get("NVIDIA_API_KEY")
GOOGLE_TOKEN = os.environ.get("GOOGLE_TOKEN")
UNSPLASH_KEY = os.environ.get("UNSPLASH_KEY")
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")

# ================= NVIDIA =================
client = OpenAI(
    api_key=NVIDIA_API_KEY,
    base_url="https://integrate.api.nvidia.com/v1"
)

# ================= AUTH =================
def authenticate():
    creds_dict = json.loads(GOOGLE_TOKEN)
    return Credentials.from_authorized_user_info(creds_dict)

# ================= BLOG ROTATION =================
def get_blog_id():
    return random.choice(BLOG_IDS)

# ================= TRENDING =================
def get_trending_topics():
    try:
        url = "https://trends.google.com/trending/rss?geo=IN"
        root = ET.fromstring(requests.get(url).content)
        return [item.text for item in root.findall(".//item/title")]
    except:
        return ["trending topics"]

# ================= NEWS =================
def get_news():
    try:
        url = f"https://newsapi.org/v2/top-headlines?country=in&pageSize=10&apiKey={NEWS_API_KEY}"
        res = requests.get(url).json()
        return [a["title"] for a in res.get("articles", []) if a.get("title")]
    except:
        return ["latest news"]

# ================= LOW COMPETITION =================
def low_comp_keyword(topic):
    suffix = random.choice([
        "for beginners",
        "step by step",
        "full guide",
        "explained simply",
        "without investment"
    ])
    return topic + " " + suffix

# ================= IMAGE =================
def get_image(query):
    try:
        url = f"https://api.unsplash.com/photos/random?query={query}&client_id={UNSPLASH_KEY}"
        return requests.get(url).json()["urls"]["regular"]
    except:
        return None

# ================= HUMANIZER =================
def humanize(text):
    phrases = ["Honestly,", "I think", "To be real,", "In my opinion,"]
    parts = text.split(". ")

    for i in range(0, len(parts), 3):
        parts[i] = random.choice(phrases) + " " + parts[i]

    return ". ".join(parts).replace("do not", "don't").replace("cannot", "can't")

def add_story(text):
    return random.choice([
        "I remember when I first saw something like this...",
        "Not gonna lie, this surprised me...",
        "This reminded me of something I experienced..."
    ]) + "<br><br>" + text

# ================= GENERATOR =================
def generate(topic, mode):

    if mode == "morning":
        topic = ", ".join(get_news()[:5])
        prompt = f"Write a blog on these news: {topic}"

    elif mode == "night":
        topic = random.choice(get_trending_topics())
        prompt = f"Write a viral blog on: {topic}"

    elif mode == "evening":
        prompt = "Write about trending AI tools"

    else:
        prompt = f"Write a story about {topic}"

    prompt += f"""

SEO RULES:
- Use keyword: {topic}
- Add headings
- Use keyword naturally

STYLE:
- human tone
- casual
- add opinions
"""

    res = client.chat.completions.create(
        model="meta/llama-3.1-70b-instruct",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
        max_tokens=1200
    )

    return res.choices[0].message.content

# ================= FORMAT =================
def format_blog(content, keyword):
    lines = content.split("\n")
    title = lines[0].replace("#", "").strip() + " (2026 Guide)"
    body = "<br>".join(lines[1:])

    img = get_image(keyword)
    if img:
        body = f'<img src="{img}" style="width:100%;border-radius:10px;"><br><br>' + body

    # 💰 MONETIZATION (AFFILIATE PLACEHOLDER)
    affiliate = """
    <br><br>
    👉 Check best tools here: https://amzn.to/YOUR-LINK  
    👉 Recommended resources: https://your-affiliate-link.com
    """

    return title, body + affiliate

# ================= PUBLISH =================
def publish(title, content):
    service = build("blogger", "v3", credentials=authenticate())

    service.posts().insert(
        blogId=get_blog_id(),
        body={
            "title": title,
            "content": content,
            "labels": ["Trending", "SEO", "AI"]
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
        topic = "trending topics"

    keyword = low_comp_keyword(topic)

    content = generate(keyword, mode)
    content = humanize(content)
    content = add_story(content)

    title, body = format_blog(content, keyword)
    publish(title, body)

if __name__ == "__main__":
    run()
