import os
import requests
import feedparser
import random
from blogger_post import publish_post

# =========================
# NVIDIA API SETTINGS
# =========================

API_KEY = os.getenv("NVIDIA_API_KEY")

MODEL = "meta/llama-3.1-70b-instruct"

# =========================
# RSS FEEDS
# =========================

feeds = {
    "tech": "https://feeds.feedburner.com/TechCrunch/",
    "entertainment": "https://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml",
    "world": "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml"
}

# =========================
# HORROR STORY TOPICS
# =========================

horror_prompts = [
    "A haunted hotel room",
    "The ghost inside a school",
    "Midnight train horror mystery",
    "A cursed village forest",
    "A terrifying abandoned hospital"
]

# =========================
# GET RANDOM TOPIC
# =========================

def get_topic(category):

    feed = feedparser.parse(feeds[category])

    entry = random.choice(feed.entries)

    return entry.title

# =========================
# GENERATE BLOG USING NVIDIA AI
# =========================

def generate_blog(topic, niche):

    prompt = f"""
Write a high-quality human-style blog article.

TOPIC:
{topic}

NICHE:
{niche}

RULES:
- conversational tone
- SEO optimized
- engaging introduction
- headings and subheadings
- natural writing style
- informative and interesting
- 1000+ words
- conclusion section
- FAQ section
"""

    response = requests.post(
        "https://integrate.api.nvidia.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "top_p": 0.9,
            "max_tokens": 1800
        }
    )

    data = response.json()

    print(data)

    if "choices" not in data:
        print("NVIDIA API ERROR")
        return

    article = data["choices"][0]["message"]["content"]

    publish_post(topic, article)

    print(f"Posted Successfully: {topic}")

# =========================
# MAIN BOT WORKFLOW
# =========================

def run_bot():

    # TECH BLOG
    tech_topic = get_topic("tech")
    generate_blog(tech_topic, "Technology")

    # ENTERTAINMENT BLOG
    entertainment_topic = get_topic("entertainment")
    generate_blog(entertainment_topic, "Entertainment")

    # HORROR STORY
    horror_topic = random.choice(horror_prompts)
    generate_blog(horror_topic, "Horror Story")

    # TRENDING NEWS
    world_topic = get_topic("world")
    generate_blog(world_topic, "Trending News")

# =========================
# START BOT
# =========================

if __name__ == "__main__":
    run_bot()
