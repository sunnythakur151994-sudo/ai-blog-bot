print("Bot Started")
from blogger_post import publish_post

title = "My First AI Blog"

content = """
<h1>Hello World</h1>

<p>This blog was automatically posted using GitHub Actions and Python.</p>
"""

publish_post(title, content)
