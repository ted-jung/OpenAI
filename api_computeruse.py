import os
from openai import OpenAI


client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    organization=os.environ.get("OPENAI_ORGANIZATION"),
    project=os.environ.get("OPENAI_PROJECT")
)

response = client.responses.create(
    model="computer-use-preview",
    tools=[{
        "type": "computer_use_preview",
        "display_width": 1024,
        "display_height": 768,
        "environment": "browser" # other possible values: "mac", "windows", "ubuntu"
    }],    
    input=[
        {
          "role": "user",
          "content": [
            {
              "type": "text",
              "text": "Check the latest OpenAI news on bing.com."
            }
            # Optional: include a screenshot of the initial state of the environment
            # {
            #     type: "input_image",
            #     image_url: f"data:image/png;base64,{screenshot_base64}"
            # }
          ]
        }
    ],
    reasoning={
        "summary": "concise",
    },
    truncation="auto"
)

print(response.output)