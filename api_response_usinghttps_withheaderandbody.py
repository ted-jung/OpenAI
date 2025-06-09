
import requests
import os
import json

from urllib import response


# request with header and body
ted_url = "https://api.openai.com/v1/models"
ted_header = {
    "Authorization": f"Bearer {os.environ.get("OPENAI_API_KEY")}",
    "Content-Type": "application/json",
    "OpenAI-Organization": os.environ.get("OPENAI_ORGANIZATION"),
    "OpenAI-Project": os.environ.get("OPENAI_PROJECT_ID"),
}

ted_body = [{
        "model": "gpt-4o-mini",
        "input": [{"role": "user", "content": "How do I check if a Python object is an instance of a class?"}]
}]

response = requests.get(ted_url, headers=ted_header, json=ted_body, timeout=5)

print(str(response)+"\n\n")
print(response.headers)

for ted in response.headers:
    print(ted)



# admin request with header and body
ted_ratelimit_url = f"https://api.openai.com/v1/organization/projects/{os.environ.get("OPENAI_PROJECT_ID")}/rate_limits"
ted_ratelimit_header = {
    "Authorization": f"Bearer {os.environ.get("OPENAI_ADMIN_KEY")}",
    "Content-Type": "application/json"
}

response = requests.get(ted_ratelimit_url, headers=ted_ratelimit_header, timeout=5)

print(str(response)+"\n\n")
print(response.headers, end="\n\n")
print(response.text, end="\n\n")
ted_json = json.loads(response.text)

for ted in ted_json['data']:
    print(f"{ted.get("id)")}-{ted.get("model")} -{ted.get("max_requests_per_1_minute")} ")

