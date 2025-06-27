# =============================================================================
# Title: RunHooks (AgentHooks) for 
# Writer: Ted Jung
# Created: 27, Jun 2025
# Updated: 27, Jun 2025
# Desription: 
#       When debugging, logs, dashboards, performance tuning.
#       When intelligent control over agent execution.
# =============================================================================


import asyncio

from agents import Agent, Runner, function_tool, RunHooks, RunResult



# — Define tools —
@function_tool
def hotel_finder(location: str, budget: str) -> str:
    return """🏨 1. **Benikea Haeundae Hotel** – Close to Haeundae Beach and popular historical sites.
2. **Haeundae Centum Hotel** – Offers easy access to both beaches and cultural landmarks.
3. **Lotte Hotel Busan** – Slightly luxury but often available at mid-range prices with excellent amenities."""

@function_tool
def place_finder(location: str, interest: str) -> str:
    return """Gamcheon Culture Village: This vibrant hillside village, often called the "Machu Picchu of Busan," is a visual delight. It's a former refugee settlement that has been transformed into an artistic and colorful community with brightly painted houses, narrow alleys, quirky sculptures, and murals at every turn. You can wander through its maze-like streets, discover hidden cafes and shops, and enjoy fantastic panoramic views of the city and the sea. It's a truly unique and Instagram-worthy experience.

Haedong Yonggungsa Temple: This Buddhist temple is incredibly special because it's one of the few in Korea located right on the coastline. Perched on cliffs overlooking the East Sea, it offers breathtaking ocean views and the sounds of crashing waves alongside its beautiful architecture. It's especially stunning during sunrise. The journey to the temple itself, often involving a walk through a pine grove and down 108 stairs, adds to its serene and spiritual atmosphere."""



# — Define agents —
# instructions is an important to get a good answer
hotel_agent = Agent(
    name="HotelFinderAgent", 
    tools=[hotel_finder], 
    instructions="Find two hotels close to beach. Add your pre-trained knowledge if the answer is too much simple",
    model="gpt-4.1-nano"
)
place_agent = Agent(
    name="PlaceFinderAgent", 
    tools=[place_finder], 
    instructions="Find two tourist places. Add your pre-trained knowledge if the answer is too much simple",
    model="gpt-4.1-nano"
)
orchestrator = Agent(
    name="TourOrchestrator",
    handoffs=[hotel_agent, place_agent],
    instructions="Plan a tour: use hotel_finder and place_finder in order.",
    model="gpt-4.1-nano"
)



# — Create hooks to capture events —
class MyHooks(RunHooks):
    def __init__(self):
        self.tool_calls = []
        self.handoffs = []

    async def on_tool_end(self, context, agent, tool, result: str):
        self.tool_calls.append((agent.name, tool.name, result))

    async def on_handoff(self, context, from_agent, to_agent):
        self.handoffs.append((from_agent.name, to_agent.name))


# — Run with hooks When the use-cases (Observability/Monitoring/Auditing...)—

async def main():
    hooks = MyHooks()
    result = await Runner.run(
        orchestrator, 
        "Plan a 2‑day historical tour in Busan on a mid‑range budget.", 
        hooks=hooks
    )

    # Final itinerary
    print("FINAL PLAN:\n", result.final_output, "\n")

    # Tool-level outputs

    print("TOOL CALLS:", hooks.tool_calls)
    print("HANDOFFS:", hooks.handoffs)

    # for tool, out in hooks.tool_calls:
    #     print(f"- {tool}: {out}")

    # Agent handoffs
    print("\nHANDOFFS:")
    for src, dst in hooks.handoffs:
        print(f"- {src} → {dst}")

if __name__ == "__main__":
    asyncio.run(main())
