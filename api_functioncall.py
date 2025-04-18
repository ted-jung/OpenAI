import os
import json
import requests
import time

from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    organization=os.environ.get("OPENAI_ORGANIZATION"),
    project=os.environ.get("OPENAI_PROJECT")
)


def get_weather(latitude, longitude):
    response = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m")
    data = response.json()
    return data['current']['temperature_2m']

def call_funtion(name, args):
    if name == "get_weather":
        return get_weather(**args)


tools = [{
    "type": "function",
    "name": "get_weather",
    "description": "Get current temperature for provided coordinates in celsius.",
    "parameters": {
        "type": "object",
        "properties": {
            "latitude": {"type": "number"},
            "longitude": {"type": "number"}
        },
        "required": ["latitude", "longitude"],
        "additionalProperties": False
    },
    "strict": True
}]

input_messages = [{"role": "user", "content": "What's the weather like in Paris today?"}]

response = client.responses.create(
    model="gpt-4.1-nano",
    input=input_messages,
    tools=tools,
)


for tool_call in response.output:
    if tool_call.type != "function_call":
        continue

    name = tool_call.name
    args = json.loads(tool_call.arguments)

    result = call_funtion(name, args)
    input_messages.append({
        "type": "function_call_output",
        "call_id": tool_call.call_id,
        "output": str(args)
    })


input_messages.append(tool_call)
input_messages.append({
    "type": "function_call_output",
    "call_id": tool_call.call_id,
    "output": str(result)
})

response_2 = client.responses.create(
    model="gpt-4.1-nano",
    input=input_messages,
    tools=tools,
    # stream=True
)


# with streaming:
# for event in response_2:
#     print(event)

# without streaming:
print(response_2.output_text)


# # assistant의 응답을 messages에 추가
# assistant_message = completion.choices[0].message
# messages.append(assistant_message)

# # tool이 호출되었다면
# if assistant_message.tool_calls:
#     # 각 tool call에 대해
#     for tool_call in assistant_message.tool_calls:
#         # tool 함수 실행
#         if tool_call.function.name == "get_weather":
#             args = json.loads(tool_call.function.arguments)
#             result = get_weather(args["latitude"], args["longitude"])
            
#             # tool의 응답을 messages에 추가
#             messages.append({
#                 "role": "tool",
#                 "tool_call_id": tool_call.id,
#                 "content": str(result)
#             })

# # 최종 응답 생성
# completion_2 = client.chat.completions.create(
#     model="gpt-4.1-nano",  # 모델 버전 업데이트
#     messages=messages
# )

# print(completion_2.choices[0].message.content)