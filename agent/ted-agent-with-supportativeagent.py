# =============================================================================
# Title: agents-with-supportativeagent.py
# Writer: Ted Jung
# Created: 17, Jun 2025
# Desription: 
#   1. Create Agent for the outline of a story(sci-fi)
#   2. Check the outline profitable on not
#   3. If not profitable, handoff to the other agent to fix
#   4. If profitable, return the outline and give it to another agent to write the story
#      return the story and print it.
# =============================================================================

import asyncio
import trace
from pydantic import BaseModel
from agents import (
    Agent, 
    Runner, 
    TResponseInputItem, 
    handoff, 
    RunContextWrapper,
    trace,
    ItemHelpers,
    handoffs,
)


class Profitable(BaseModel):
    is_profitable: bool
    is_scifi: bool
    reason: str

# Three agents outline_builder, outline_checker, story_writer_basedon_builder
story_outline_agent = Agent(
    name="story_outline_agent",
    model="gpt-4.1-nano",
    instructions="""
        You are an expert outline builder of story. make an outline of the story with given message.
        If the given message is not related scifi. then, response not profitable with reason.
    """
)

# if not profitable on the message, it will fail
outline_checker_agent = Agent(
    name="outline_checker_agent",
    model="gpt-4.1-nano",
    instructions="Read the given story outline, and judge the quality. Also, determine if it is a scifi story.",
    output_type=Profitable,
)


# if profitable, write full story based on the outline
story_builder_agent = Agent(
    name="story_agent",
    model="gpt-4.1-nano",
    instructions="Write a short story based on the given outline.",
    output_type=str,
)



async def ted_main():

    msg = input("What type of story do you want to write?...")

    with trace("Ted's story"):
        response1 = await Runner.run(story_outline_agent, msg)
        print("Outline generated")

        response2 = await Runner.run(outline_checker_agent, response1.final_output)


        if not response2.final_output.is_profitable:
            print(f"error:{response2.final_output.reason}")

        if not response2.final_output.is_scifi:
            print(f"error:{response2.final_output.reason}")


        for item in response2.new_items:
            text = ItemHelpers.text_message_output(item)
            if text:
                print(f"  - Translation step: {text}")


        response3 = await Runner.run(story_builder_agent, response1.final_output)

        print(f"Final story: {response3.final_output}")



if __name__ == "__main__":
    asyncio.run(ted_main())