import os
import json
import random
import requests
from openai import OpenAI
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# ================= MULTI BLOG =================
BLOG_IDS = [
    "8997390388821877620",
    # add more blog IDs here
]

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

# ================= BLOG ROTATION =================
def get_blog():
    return random.choice(BLOG_IDS)

# ================= TOPIC =================
def get_topic():
    try:
        url = f"https://newsapi.org/v2/top-headlines?country=in&pageSize=5&apiKey={NEWS_API_KEY}"
        res = requests.get(url).json()
        return random.choice([a["title"] for a in res.get("articles", []) if a.get("title")])
    except:
        return "latest trending topic"

# ================= HIGH CTR TITLE =================
def generate_titles(topic):

    prompt = f"""
Generate 5 HIGH CTR blog titles.

Rules:
- curiosity driven
- emotional
- SEO friendly
- clickbait but realistic

Topic: {topic}
"""

    res = client.chat.completions.create(
        model="meta/llama-3.1-70b-instruct",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9,
        max_tokens=200
    )

    titles = res.choices[0].message.content.split("\n")
    return random.choice([t for t in titles if t.strip()])

# ================= CONTENT =================
def generate_blog(topic, title):

    prompt = f"""
Write a blog.

Title: {title}

Rules:
- human tone
- engaging
- no markdown
- headings
- storytelling
"""

    res = client.chat.completions.create(
        model="meta/llama-3.1-70b-instruct",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9,
        max_tokens=1500
    )

    return res.choices[0].message.content

# ================= IMAGE =================
def get_image(query):
    try:
        url = f"https://api.unsplash.com/photos/random?query={query}&client_id={UNSPLASH_KEY}"
        return requests.get(url).json()["urls"]["regular"]
    except:
        return None

# ================= FORMAT =================
def format_blog(content, title):

    lines = content.split("\n")

    html = f"<h1 style='font-weight:bold'>{title}</h1>"

    count = 0

    for line in lines:

        line = line.strip()
        if not line:
            continue

        if len(line) < 80 and line[0].isupper():
            html += f"<h2>{line}</h2>"
        else:
            html += f"<p>{line}</p>"
            count += 1

            if count % 2 == 0:
                img = get_image(line[:30])
                if img:
                    html += f'<img src="{img}" style="width:100%">'

    # 🔗 INTERNAL BACKLINK SYSTEM
    html += """
    <hr>
    <h3>Read More</h3>
    <ul>
        <li>Latest AI Tools Guide</li>
        <li>Top Trending News</li>
        <li>Best Stories Today</li>
    </ul>
    """

    return html

# ================= BLOGGER =================
def post_blogger(title, content):

    service = build("blogger", "v3", credentials=authenticate())

    service.posts().insert(
        blogId=get_blog(),
        body={
            "title": title,
            "content": content
        }
    ).execute()

    print("✅ Posted:", title)

# ================= MAIN =================
def run():

    topic = get_topic()

    print("Generating CTR title...")
    title = generate_titles(topic)

    print("Generating content...")
    content = generate_blog(topic, title)

    print("Formatting...")
    html = format_blog(content, title)

    print("Posting...")
    post_blogger(title, html)

if __name__ == "__main__":
    run()
