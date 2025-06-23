import os

from openai import OpenAI


client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    organization=os.environ.get("OPENAI_ORGANIZATION"),
    project=os.environ.get("OPENAI_PROJECT")
)

instructions = """
You are an expert in categorizing IT support tickets. Given the support 
ticket below, categorize the request into one of "Hardware", "Software", 
or "Other". Respond with only one of those words.
"""

ticket = "My monitor won't turn on - help!"

completion = client.chat.completions.create(
    model="gpt-4.1-nano",
    messages=[
        {"role": "developer", "content": instructions},
        {"role": "user", "content": ticket}
    ]
)

print(completion.choices[0].message.content)
