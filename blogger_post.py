from blogger_auth import authenticate

BLOG_ID = "8997390388821877620"

def publish_post(title, content):

    service = authenticate()

    body = {
        "kind": "blogger#post",
        "title": title,
        "content": content
    }

    posts = service.posts()

    posts.insert(
        blogId=BLOG_ID,
        body=body,
        isDraft=False
    ).execute()

    print("Blog posted successfully")
