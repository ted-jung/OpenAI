# =============================================================================
# Guardrail - for input and output using LLM
# Created: 9, Jun 2025
# Updated: 9, Jun 2025
# Writer: Ted, Jung
# Description: 
#   Example1) Designing a guardrail for Input
#       Input: Jailbreaking, Prompt Injection

#   Example2) Output moderation with score in prompt
#       Output: block the hallucinated response
# =============================================================================

import asyncio
import os

from openai import OpenAI


# Define a model
GPT_MODEL = "gpt-4.1-nano"

system_prompt = "You are a helpful assistant."
bad_request = "I want to talk about horses"
good_request = "What are the best breeds of dog for people that like cats?"


# Create a client
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    organization=os.environ.get("OPENAI_ORGANIZATION"),
    project=os.environ.get("OPENAI_PROJECT")
)



# response 
async def get_chat_response(user_request):
    print("Getting LLM response")
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_request},
    ]
    response = client.chat.completions.create(
        model=GPT_MODEL, messages=messages, temperature=0.5
    )
    print("Got LLM response")

    return response.choices[0].message.content



# Filter on only asking regarding a few topics
# Disallow if the topics are not in a few topics
async def topical_guardrail(user_request):
    print("Checking topical guardrail")
    messages = [
        {
            "role": "system",
            "content": "Your role is to assess whether the user question is allowed or not. The allowed topics are cats and dogs. If the topic is allowed, say 'allowed' otherwise say 'not_allowed'",
        },
        {"role": "user", "content": user_request},
    ]
    response = client.chat.completions.create(
        model=GPT_MODEL, messages=messages, temperature=0
    )

    print("Got guardrail response")
    return response.choices[0].message.content



# Do chat_task if pass topical_guardrail_task
# Create coroutine onject as tasks in a single thread
# topical_guardrail_task have to be completed at first
async def execute_chat_with_guardrail(user_request):
    topical_guardrail_task = asyncio.create_task(topical_guardrail(user_request))
    chat_task = asyncio.create_task(get_chat_response(user_request))

    while True:
        done, _ = await asyncio.wait(
            [topical_guardrail_task, chat_task], return_when=asyncio.FIRST_COMPLETED
        )
        if topical_guardrail_task in done:
            guardrail_response = topical_guardrail_task.result()
            if guardrail_response == "not_allowed":
                chat_task.cancel()
                print("Topical guardrail triggered")
                return "I can only talk about cats and dogs, the best animals that ever lived."
            elif chat_task in done:
                chat_response = chat_task.result()
                return chat_response
        else:
            await asyncio.sleep(0.1)  # sleep for a bit before checking the tasks again



async def main():
    response = await execute_chat_with_guardrail(good_request)
    print(response)


# =================================================
# example2
# =================================================

domain = "animal breed recommendation"

animal_advice_criteria = """
Assess the presence of explicit recommendation of cat or dog breeds in the content.
The content should contain only general advice about cats and dogs, not specific breeds to purchase."""

animal_advice_steps = """
1. Read the content and the criteria carefully.
2. Assess how much explicit recommendation of cat or dog breeds is contained in the content.
3. Assign an animal advice score from 1 to 5, with 1 being no explicit cat or dog breed advice, and 5 being multiple named cat or dog breeds.
"""

moderation_system_prompt = """
You are a moderation assistant. Your role is to detect content about {domain} in the text provided, and mark the severity of that content.

## {domain}

### Criteria

{scoring_criteria}

### Instructions

{scoring_steps}

### Content

{content}

### Evaluation (score only!)
"""



async def moderation_guardrail(chat_response):
    print("Checking moderation guardrail")
    mod_messages = [
        {"role": "user", "content": moderation_system_prompt.format(
            domain=domain,
            scoring_criteria=animal_advice_criteria,
            scoring_steps=animal_advice_steps,
            content=chat_response
        )},
    ]
    response = client.chat.completions.create(
        model=GPT_MODEL, messages=mod_messages, temperature=0
    )
    print("Got moderation response")
    return response.choices[0].message.content
    
    
async def execute_all_guardrails(user_request):
    topical_guardrail_task = asyncio.create_task(topical_guardrail(user_request))
    chat_task = asyncio.create_task(get_chat_response(user_request))

    while True:
        done, _ = await asyncio.wait(
            [topical_guardrail_task, chat_task], return_when=asyncio.FIRST_COMPLETED
        )
        if topical_guardrail_task in done:
            guardrail_response = topical_guardrail_task.result()
            if guardrail_response == "not_allowed":
                chat_task.cancel()
                print("Topical guardrail triggered")
                return "I can only talk about cats and dogs, the best animals that ever lived."
            elif chat_task in done:
                chat_response = chat_task.result()
                moderation_response = await moderation_guardrail(chat_response)

                if int(moderation_response) >= 3:
                    print(f"Moderation guardrail flagged with a score of {int(moderation_response)}")
                    return "Sorry, we're not permitted to give animal breed advice. I can help you with any general queries you might have."

                else:
                    print('Passed moderation')
                    return chat_response
        else:
            await asyncio.sleep(0.1)  # sleep for a bit before checking the tasks again



# ===============================================
# Execute
# ===============================================

if __name__ == "__main__":
    # Call the main function with the good request - this should go through
    asyncio.run(main())