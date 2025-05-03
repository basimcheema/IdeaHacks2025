import os
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",
)

response = client.chat.completions.create(
    model="deepseek/deepseek-chat:free",
    messages=[
	{"role": "system", "content": "You are a coding assistant that talks like a pirate."},
	{"role": "user", "content": "How do I check if a Python object is an instance of a class?"},
    ]
)

print(response.choices[0].message.content)
