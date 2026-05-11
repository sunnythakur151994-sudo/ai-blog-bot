import os
import json
import random
import requests
from datetime import datetime
from openai import OpenAI
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# ================= CONFIG =================
BLOG_ID = "8997390388821877620"

NVIDIA_API_KEY = os.environ.get("NVIDIA_API_KEY")
GOOGLE_TOKEN = os.environ.get("GOOGLE_TOKEN")
UNSPLASH_KEY = os.environ.get("UNSPLASH_KEY")

# ================= NVIDIA =================
client = OpenAI(
    api_key=NVIDIA_API_KEY,
    base_url="https://integrate.api.nvidia.com/v1"
)

# ================= AUTH =================
def authenticate():
    creds_dict = json.loads(GOOGLE_TOKEN)
    return Credentials.from_authorized_user_info(creds_dict)

# ================= IMAGE =================
def get_image(query):
    try:
        url = f"https://api.unsplash.com/photos/random?query={query}&client_id={UNSPLASH_KEY}"
        return requests.get(url).json()["urls"]["regular"]
    except:
        return None

# ================= HUMANIZER =================
def humanize_text(text):
    phrases = ["Honestly,", "I think", "To be real,", "In my opinion,"]
    parts = text.split(". ")

    for i in range(0, len(parts), 3):
        parts[i] = random.choice(phrases) + " " + parts[i]

    return ". ".join(parts)

def add_story(text):
    stories = [
        "I remember when I first saw something like this...",
        "Not gonna lie, this surprised me...",
        "This reminded me of something I experienced..."
    ]
    return random.choice(stories) + "<br><br>" + text

# ================= GENERATE =================
def generate_blog(topic, mode):

    if mode == "morning":
        prompt = f"""
Write a blog on top 10 current news.

- Explain each news
- Add your opinion
"""

    elif mode == "afternoon":
        prompt = f"""
Write a human-like story about {topic}
"""

    elif mode == "evening":
        prompt = f"""
Write about trending AI tools and technologies
"""

    else:
        prompt = f"""
Write a trending blog on {topic}
"""

    prompt += """

Write like a human:
- casual tone
- use "I think", "honestly"
- mix sentence length
- ask questions
"""

    response = client.chat.completions.create(
        model="meta/llama-3.1-70b-instruct",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
        max_tokens=1200
    )

    return response.choices[0].message.content

# ================= FORMAT =================
def format_blog(content):
    lines = content.split("\n")
    title = lines[0].replace("#", "").strip()
    body = "<br>".join(lines[1:])

    img = get_image(title[:50])
    if img:
        body = f'<img src="{img}" style="width:100%;border-radius:10px;"><br><br>' + body

    return title, body

# ================= PUBLISH =================
def publish(title, content):
    creds = authenticate()
    service = build("blogger", "v3", credentials=creds)

    post = {
        "title": title,
        "content": content,
        "labels": ["AI", "Tech"]
    }

    service.posts().insert(blogId=BLOG_ID, body=post).execute()
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

    print("Mode:", mode)

    content = generate_blog(topic, mode)
    content = humanize_text(content)
    content = add_story(content)

    title, body = format_blog(content)
    publish(title, body)

if __name__ == "__main__":
    run()
