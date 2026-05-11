import os
import requests
import feedparser
import random
from blogger_post import publish_post

API_KEY = os.getenv("NVIDIA_API_KEY")

MODEL = "meta/llama3-70b-instruct"

# ----------------------------
# NEWS SOURCES
# ----------------------------

feeds = {
    "tech": "https://feeds.feedburner.com/TechCrunch/",
    "entertainment": "https://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml",
    "world": "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml"
}

# ----------------------------
# HORROR STORY PROMPTS
# ----------------------------

horror_prompts = [
    "A haunted hotel room",
    "The ghost inside a school",
    "Midnight train horror mystery",
    "A cursed village forest",
    "A terrifying abandoned hospital",
]

# ----------------------------
# GET TRENDING TOPIC
# ----------------------------

def get_topic(category):

    feed = feedparser.parse(feeds[category])

    entry = random.choice(feed.entries)

    return entry.title

# ----------------------------
# NVIDIA AI BLOG GENERATION
# ----------------------------

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
- add opinions naturally
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

    article = data["choices"][0]["message"]["content"]

    publish_post(topic, article)

    print(f"Posted Successfully: {topic}")

# ----------------------------
# MAIN AUTOMATION
# ----------------------------

def run_bot():

    # TECH BLOG
    tech_topic = get_topic("tech")
    generate_blog(tech_topic, "Technology")

    # ENTERTAINMENT BLOG
    ent_topic = get_topic("entertainment")
    generate_blog(ent_topic, "Entertainment")

    # HORROR STORY
    horror = random.choice(horror_prompts)
    generate_blog(horror, "Horror Story")

    # TRENDING WORLD NEWS
    world_topic = get_topic("world")
    generate_blog(world_topic, "Trending News")

# ----------------------------
# START BOT
# ----------------------------

if __name__ == "__main__":
    run_bot()
