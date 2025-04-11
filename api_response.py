# =============================================================================
# Title: How to handle response from OpenAI API
# Writer: Ted Jung
# Date: 10, Apr 2025
# Description: 
#   there are few ways to handle the response from OpenAI API:
#   1. Using the `with_raw_response` method to get the raw response and headers.
#   2. Using the response.parse() method to get the parsed response.
#   
# =============================================================================

import os
import json

from openai import OpenAI


client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    organization=os.environ.get("OPENAI_ORGANIZATION"),
    project=os.environ.get("OPENAI_PROJECT")
)

response = client.responses.with_raw_response.create(
    model="gpt-4o-mini",
    input=[{"role": "user", "content": "How do I check if a Python object is an instance of a class?"}],
    stream=True,
)


ted_data0 = response.http_response.headers
ted_data1 = json.loads(response.text)
ted_data2 = response.parse()


for key,value in ted_data0.items():
    print(f"{key}: {value}")

for key in ted_data1:
    print(f"{key}: {ted_data1[key]}")

for key, value in ted_data2:
    print(f"{key}: {value}")


# response = client.responses.create(
#     model="gpt-4o-mini",
#     tools=[{"type": "web_search_preview"}],
#     input="what was a positive news story from today?"
# )

# print(response.output_text)