# =============================================================================
# Title: X-* metadata headers
# Writer: Ted Jung
# Date: 10, Apr 2025
# Description: 
#   This script demonstrates how to use the OpenAI API to get the X-* metadata headers.
# =============================================================================

from openai import OpenAI
import os

# client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

try:
    raw_response = client.chat.completions.with_raw_response.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": "Hello again"}
        ]
    )

    # Now you can access the headers from the raw response object
    limit_requests = raw_response.headers.get("x-ratelimit-limit-requests")

    if limit_requests:
        print(f"X-RateLimit-Limit-Requests: {limit_requests}")
    else:
        print("X-RateLimit-Limit-Requests header not found in the response.")

except Exception as e:
    print(f"An error occurred: {e}")