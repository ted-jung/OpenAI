# =============================================================================
# Title: Using httpsx to get the X-* metadata headers
# Writer: Ted Jung
# Date: 10, Apr 2025
# Description: 
#   This script demonstrates how to use the OpenAI API to get the X-* metadata headers.
#   ADMIN API KEY is required to get the rate limit.
# =============================================================================

import os 
import httpx
import json


ted_ratelimit_url = f"https://api.openai.com/v1/organization/projects/{os.environ.get("OPENAI_PROJECT_ID")}/rate_limits"
ted_ratelimit_header = {
    "Authorization": f"Bearer {os.environ.get("OPENAI_ADMIN_KEY")}",
    "Content-Type": "application/json"
}

response = httpx.get(ted_ratelimit_url, headers=ted_ratelimit_header, timeout=5)
print(str(response) + "\n\n")

ted_json = json.loads(response.text)
for ted in ted_json.get("data"):
    print(ted)

