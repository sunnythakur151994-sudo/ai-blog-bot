import os
import json
from openai import OpenAI
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# =========================
# 🔐 CONFIG SECTION
# =========================

# 👉 PASTE YOUR BLOG ID HERE
BLOG_ID = "PASTE_YOUR_BLOG_ID_HERE"

# 👉 NVIDIA API KEY (put in environment variable for safety)
NVIDIA_API_KEY = os.environ.get("NVIDIA_API_KEY")

# =========================
# 🤖 AI CLIENT (NVIDIA)
# =========================

client = OpenAI(
    api_key=NVIDIA_API_KEY,
    base_url="https://integrate.api.nvidia.com/v1"
)

# =========================
# 🔐 GOOGLE AUTH (ENV TOKEN)
# =========================

def authenticate():
    token_str = os.environ.get("GOOGLE_TOKEN")

    if not token_str:
        raise Exception("❌ GOOGLE_TOKEN not found in environment variables")

    creds_dict = json.loads(token_str)
    creds = Credentials.from_authorized_user_info(creds_dict)

    return creds

# =========================
# ✍️ GENERATE BLOG
# =========================

def generate_blog(topic):
    response = client.chat.completions.create(
        model="meta/llama-3.1-70b-instruct",
        messages=[
            {
                "role": "user",
                "content": f"""
Write a high-quality, SEO-optimized blog post on: {topic}

Include:
- Catchy title
- Introduction
- 5-7 headings
- Conclusion
- Make it engaging and human-like
"""
            }
        ],
        temperature=0.7,
        max_tokens=1200
    )

    return response.choices[0].message.content

# =========================
# 🧹 FORMAT BLOG
# =========================

def format_blog(content):
    lines = content.split("\n")

    # First line = title
    title = lines[0].replace("#", "").strip()

    # Rest = body
    body = "<br>".join(lines[1:])

    return title, body

# =========================
# 🌐 PUBLISH TO BLOGGER
# =========================

def publish_post(title, content):
    creds = authenticate()
    service = build("blogger", "v3", credentials=creds)

    post = {
        "title": title,
        "content": content
    }

    service.posts().insert(
        blogId=BLOG_ID,
        body=post
    ).execute()

    print(f"✅ Posted: {title}")

# =========================
# 🔁 MAIN BOT FUNCTION
# =========================

def run_bot():
    topic = "Latest AI Tools 2026"   # you can make this dynamic later

    print("⚡ Generating blog...")
    content = generate_blog(topic)

    print("🧹 Formatting blog...")
    title, body = format_blog(content)

    print("🚀 Publishing blog...")
    publish_post(title, body)

# =========================
# ▶️ RUN
# =========================

if __name__ == "__main__":
    run_bot()
