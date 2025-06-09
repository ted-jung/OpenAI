# =============================================================================
# Title: OpenAI API Rate Limit Handling with Retry
# Writer: Ted Jung
# Date: 10, Apr 2025
# Description: 
#   This script demonstrates how to use the OpenAI API with a retry mechanism for rate limiting.
#   It uses the `tenacity` library to implement exponential backoff for retrying requests.
# =============================================================================

from tenacity import(
    retry,
    stop_after_attempt,
    wait_random_exponential
)
import os
import openai


# retry decorator to handle rate limiting
@retry(wait=wait_random_exponential(multiplier=1, min=4, max=10), stop=stop_after_attempt(5))
def completion_with_backoff(**kwargs):
    client = openai.OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        organization=os.getenv("OPENAI_ORG_ID"),
        project=os.getenv("OPENAI_PROJECT_ID"),
    )

    return client.chat.completions.create(**kwargs)

for _ in range(5):
    response = completion_with_backoff (
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "user",
                            "content": "Once upon a time, ",
                        }],
                    max_tokens=20
            )

    print(response, end="\n\n")
    print(response.choices[0].message.content, end="\n\n")



# for _ in range(100):
#     client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[
#             {
#                 "role": "user",
#                 "content": "Hello",
#             }],
#         max_tokens=10,
#     )