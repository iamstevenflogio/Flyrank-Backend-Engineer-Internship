# Python

import os
from openai import OpenAI

client = OpenAI(base_url=os.environ["https://openrouter.ai/api/v1"], api_key=os.environ["sk-or-v1-e473cbb53c479739c37f62fa74"])

res = client.chat.completions.create(
model=os.environ["openrouter/free"]
messages=[{"role": "user", "content": "Reply with exactly the word: ready"}]
)
print(res.choices[0].message.content)
