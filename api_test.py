import os
import json
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    organization=os.environ.get("OPENAI_ORGANIZATION"),
    project=os.environ.get("OPENAI_PROJECT")
)

response = client.responses.create(
    model="gpt-4o-mini",
    input=[
        {"role": "system", "content": "You are a helpful math tutor. Guide the user through the solution step by step."},
        {"role": "user", "content": "how can I solve 8x + 7 = -23"}
    ],
    text={
        "format": {
            "type": "json_schema",
            "name": "math_reasoning",
            "schema": {
                "type": "object",
                "properties": {
                    "steps": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "explanation": { "type": "string" },
                                "output": { "type": "string" }
                            },
                            "required": ["explanation", "output"],
                            "additionalProperties": False
                        }
                    },
                    "final_answer": { "type": "string" }
                },
                "required": ["steps", "final_answer"],
                "additionalProperties": False
            },
            "strict": True
        }
    }
)

print(type(response))

math_reasoning = json.loads(response.output_text)

print(type(math_reasoning))


print(math_reasoning)

for event in math_reasoning["steps"]:
    print(f"Step: {event['explanation']}")
    print(f"Output: {event['output']}")

print(f"Final Answer: {math_reasoning['final_answer']}")