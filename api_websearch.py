import os
from openai import OpenAI


client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    organization=os.environ.get("OPENAI_ORGANIZATION"),
    project=os.environ.get("OPENAI_PROJECT")
)

response = client.responses.create(
        model="gpt-4o-mini",
        input=[{"role": "user", "content": "What movie won the best picture in 2025?"}],
        tools=[{
            "type": "web_search_preview",
            "search_context_size": "low"
            }
        ]
)

print(response.output_text)