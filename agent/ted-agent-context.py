# =============================================================================
# Title: Context in Agent (this is just for a example)
# Created: 23, Jun 2025
# Updated: 23, Jun 2025
# Writer: Ted, Jung
# Description:
#   Context is a media that is shared during dialog
#   Need to interface with database for consistency and integrity for budget
# =============================================================================

import asyncio
import random

from dataclasses import dataclass
from agents import (
    Agent, 
    RunContextWrapper, 
    Runner, 
    TResponseInputItem, 
    function_tool
)


@dataclass
class UserProfile:
    id: str
    name: str
    budget: int
    shopping_cart: list[str]


# Five function_tools to be used in Agent

@function_tool
async def get_budget(ctx: RunContextWrapper[UserProfile]):
    """
    Get the account balance of the user using the user's id and their linked bank account
    """
    print("Getting account balance")
    user_id = ctx.context.id

    # pretend we are fetching the account balance from a database

    return ctx.context.budget

@function_tool
async def increase_budget(ctx: RunContextWrapper[UserProfile]):
    """
    Add only the amount of the user requested to current budget
    """

    amount_str = input("how much budget to add? ")
    try:
        amount = int(amount_str)
    except ValueError:
        print("Invalid input. Please enter a number.")
        return ctx.context.budget

    ctx.context.budget += amount

    return ctx.context.budget


@function_tool
async def search_for_item(ctx: RunContextWrapper[UserProfile], item: str) -> str:
    """
    Search for an item in the database
    """
    print("Searching for item")
    # randomly generate a price for the item
    price = random.randint(1, 100)
    return f"Found {item} in the database for ${price}.00"

@function_tool
async def get_shopping_cart(ctx: RunContextWrapper[UserProfile]) -> list[str]:
    print("Getting shopping cart")
    return ctx.context.shopping_cart

@function_tool
async def add_to_shopping_cart(ctx: RunContextWrapper[UserProfile], items: list[str]) -> None:
    print("Adding items to shopping cart")
    ctx.context.shopping_cart.extend(items)

@function_tool
async def remove_from_shopping_cart(ctx: RunContextWrapper[UserProfile], items: list[str]) -> None:
    print("Removing items from shopping cart")
    ctx.context.shopping_cart.remove(items)
    
@function_tool
async def purchase_items(ctx: RunContextWrapper[UserProfile]) -> None:
    print("Purchasing items")
    if ctx.context.id == "ted-123":
        print("success")
    else:
        print("fail")
    
    # we could take the items from the shopping cart and purchase them using some external API
    # for now, we'll just print a message
    print(f"Successfully purchased items: {ctx.context.shopping_cart}")



# Define a specific agent for shopping
# it will try to calls to to know budget

shopping_agent = Agent[UserProfile](
    name="Shopping Assistant",
    model="gpt-4.1-nano",
    instructions=(
        "You are a shopping assistant dedicated to helping the user with their grocery shopping needs."
        "Your primary role is to assist in creating a shopping plan that fits within the user's budget."
        "Start by getting the user's budget using the tool get_budget and print it total buget."
        "If the user ask to add budget, call increase_budget then add it based on the current budget."
        "Provide suggestions for items if requested, and always aim to keep the total cost within the user's budget."
        "If the user is nearing or exceeding their budget, inform them and suggest alternatives or adjustments to the shopping list."
        "If the user authorizes it, you can purchase the items using the tool purchase_items."
    ),
    tools=[get_budget, increase_budget, search_for_item, get_shopping_cart, add_to_shopping_cart, remove_from_shopping_cart, purchase_items],
)

profile = UserProfile(id="ted-123", name="Ted", budget=0, shopping_cart=[])
print("Chatting with the shopping assistant. Type 'exit' to end the conversation.\n")

# Declare a variable of the list type

async def main():
    dialog_items: list[TResponseInputItem] = []
    while True:
        user_input = input("You: ")

        if user_input == "exit":
            print("Goodbye!")
            break

        dialog_items.append({"content": user_input, "role": "user"})

        # A run result containing all the inputs, guardrail results and the output of the last agent. 
        # Agents may perform handoffs, so we don't know the specific type of the output.
        # the method run() work with input and context

        print(f"{dialog_items} \n\n===============")
        result = await Runner.run(shopping_agent, dialog_items, context=profile)
        
        print(f"\nShopping Assistant: {result.final_output}")
        
        dialog_items = result.to_input_list()


if __name__ == "__main__":
    asyncio.run(main())