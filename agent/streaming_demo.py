# =============================================================================
# Title: OpenAI Agents Streaming Demo
# Created: 13, Jun, 2025
# Author: Ted, Jung 
# Description:
#     > streamlit run streaming_demo.py
# =============================================================================

import asyncio
import streamlit as st 
import sys
import os

from openai.types.responses import ResponseTextDeltaEvent
from agents import Agent, Runner

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(
    page_title="OpenAI Agents Streaming Demo",
    page_icon="🤖",
    layout="wide",
)

st.title("Agents Streaming Demo")
# st.write("See the streaming capabilities of OpenAI Agents with visual effects.")

with st.sidebar:
    st.header("OpenAI Agent Configuration")
    agent_name = st.text_input("Agent Name", value="Ted's Bot")
    agent_instructions = st.text_area(
        "System Instructions",
        value="You are a helpful assistant that responses should be creative and engaging",
    )

    model_options = [
        "gpt-4o-mini",
        "gpt-4.1-nano",
    ]

    example_options = [
        "",
        "Simple Chat",
        "Math Solver",
        "Creative Writing",
        "Code Debugging",
        "Give me 3 topics regarding the current poliical situation in the South Korea",
    ]

    selected_model = st.selectbox("Model", model_options, index=1)
    choosen_prompt = st.selectbox("Example Prompt", example_options)

    st.markdown("---")
    # st.markdown("Ted")


user_input = st.text_area("Your message:", value=choosen_prompt, height=100)
send_button = st.button("Send", type="primary")

response_container = st.container()

async def main(agent: Agent, user_input: str) -> None:
    response_parts = ""
    try:
        result = Runner.run_streamed(agent, input=user_input)
        async for event in result.stream_events():
            if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                # print(event.data.delta)
            
                response_parts += event.data.delta
                message_placeholder.markdown(response_parts + "|")
        message_placeholder.markdown(response_parts)
    except Exception as e:
        st.error(f"An error occurred: {e}")
        print(f"Error: {e}")



# if send_button or user_input:
if send_button:
    agent = Agent(
        name=agent_name,
        instructions=agent_instructions,
        model=selected_model,
    )

    with response_container:
        message_placeholder = st.empty()

        with st.spinner("Generating response..."):
            asyncio.run(main(agent, user_input))

        if st.button("Clear Chat", key="clear_chat"):
            response_container.empty()
            message_placeholder.empty()
            user_input = ""
            st.rerun()


# Istructions for running the demo:
# 1. Install the required packages:
#    pip install openai streamlist agents
# 2. Set your OpenAI API key in the environment variable
#    export OPENAI_API_KEY="your_openai_api_key"
# 3. Run the script:
#    python streaming_demo.py
# 4. Open the web interface in your browser at http://localhost:8501
# 5. Interact with the agent by typing messages and observing the streaming responses.
#    You can also change the agent's name, instructions, and model in the sidebar.


if not send_button:
    with response_container:
        st.info(" Enter your message and click 'Send' to see the streaming response from the agent.")
        st.markdown("""
        #### Tips:
        - Choose from the quick prompts or enter your own
        - Try complex prompts to see how the agent handles them in real-time 
        """)