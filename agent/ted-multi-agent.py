# =============================================================================
# Title: Async tasks with results from multi agents
# Created: 24, Jun 2025
# Updated: 24, Jun 2025
# Writer: Ted, Jung
# Desctipion:
#   gpt-4.1-nano does not support websearch (use 4o)
#   outline -> search -> write
# =============================================================================

import asyncio
import time

from pydantic import BaseModel
from rich.console import Console
from agents import Agent, Runner, custom_span, gen_trace_id, trace, WebSearchTool
from agents.model_settings import ModelSettings
from typing import Any

from rich.console import Console, Group
from rich.live import Live
from rich.spinner import Spinner




class ReportData(BaseModel):
    short_summary: str
    """A short 2-3 sentence summary of the findings."""

    markdown_report: str
    """The final report"""

    follow_up_questions: list[str]
    """Suggested topics to research further"""


class WebSearchItem(BaseModel):
    reason: str
    "Your reasoning for why this search is important to the query."

    query: str
    "The search term to use for the web search."


class WebSearchPlan(BaseModel):
    searches: list[WebSearchItem]
    """A list of web searches to perform to best answer the query."""


class ResearchManager:

    def __init__(self):
        self.console = Console()
        self.printer = Printer(self.console)


    async def run(self, query: str) -> None:
        trace_id = gen_trace_id()
        with trace("Research trace", trace_id=trace_id):
            self.printer.update_item(
                "trace_id",
                f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}",
                is_done=True,
                hide_checkmark=True,
            )

            self.printer.update_item(
                "starting",
                "Starting research...",
                is_done=True,
                hide_checkmark=True,
            )
            search_plan = await self._plan_searches(query)
            search_results = await self._perform_searches(search_plan)
            report = await self._write_report(query, search_results)

            final_report = f"Report summary\n\n{report.short_summary}"
            self.printer.update_item("final_report", final_report, is_done=True)

            self.printer.end()

        print("\n\n=====REPORT=====\n\n")
        print(f"Report: {report.markdown_report}")
        print("\n\n=====FOLLOW UP QUESTIONS=====\n\n")
        follow_up_questions = "\n".join(report.follow_up_questions)
        print(f"Follow up questions: {follow_up_questions}")


    async def _plan_searches(self, query: str) -> WebSearchPlan:
        PROMPT = (
            "You are a helpful research assistant. Given a query, come up with a set of web searches "
            "to perform to best answer the query. Output between 5 and 20 terms to query for."
        )
        
        planner_agent = Agent(
            name="PlannerAgent",
            instructions=PROMPT,
            model="gpt-4.1-nano",
            output_type=WebSearchPlan,
        )
        
        self.printer.update_item("planning", "Planning searches...")
        result = await Runner.run(
            planner_agent,
            f"Query: {query}",
        )
        self.printer.update_item(
            "planning",
            f"Will perform {len(result.final_output.searches)} searches",
            is_done=True,
        )
        return result.final_output_as(WebSearchPlan)


    async def _perform_searches(self, search_plan: WebSearchPlan) -> list[str]:
        with custom_span("Search the web"):
            self.printer.update_item("searching", "Searching...")
            num_completed = 0

            # multiple coroutine background search operations concurrently
            tasks = [asyncio.create_task(self._search(item)) for item in search_plan.searches]
            results = []

            # Two options
            # Option1 (wait all to be done)
            responses = await asyncio.gather(*tasks)
            for result in responses:
                if result is not None:
                    results.append(result)
                num_completed += 1

            # Option2 (process the task that arrived earliest among the tasks)
            # for task in asyncio.as_completed(tasks):
            #     result = await task
            #     if result is not None:
            #         results.append(result)
            #     num_completed += 1
            #     self.printer.update_item(
            #         "searching", f"Searching... {num_completed}/{len(tasks)} completed"
            #     )
            self.printer.mark_item_done("searching")
            return results


    async def _search(self, item: WebSearchItem) -> str | None:
        INSTRUCTIONS = (
            "You are a research assistant. Given a search term, you search the web for that term and "
            "produce a concise summary of the results. The summary must be 2-3 paragraphs and less than 300 "
            "words. Capture the main points. Write succinctly, no need to have complete sentences or good "
            "grammar. This will be consumed by someone synthesizing a report, so its vital you capture the "
            "essence and ignore any fluff. Do not include any additional commentary other than the summary "
            "itself."
        )

        search_agent = Agent(
            name="Search agent",
            model="gpt-4.1-nano",
            instructions=INSTRUCTIONS,
            tools=[WebSearchTool()],
            model_settings=ModelSettings(tool_choice="required"),
        )

        input = f"Search term: {item.query}\nReason for searching: {item.reason}"
        try:
            result = await Runner.run(
                search_agent,
                input,
            )
            return str(result.final_output)
        except Exception:
            return None

    async def _write_report(self, query: str, search_results: list[str]) -> ReportData:
        PROMPT = (
            "You are a senior researcher tasked with writing a cohesive report for a research query. "
            "You will be provided with the original query, and some initial research done by a research "
            "assistant.\n"
            "You should first come up with an outline for the report that describes the structure and "
            "flow of the report. Then, generate the report and return that as your final output.\n"
            "The final output should be in markdown format, and it should be lengthy and detailed. Aim "
            "for 5-10 pages of content, at least 1000 words."
        )

        writer_agent = Agent(
            name="WriterAgent",
            instructions=PROMPT,
            model="gpt-4.1-nano",
            output_type=ReportData,
        )


        self.printer.update_item("writing", "Thinking about report...")
        input = f"Original query: {query}\nSummarized search results: {search_results}"
        result = Runner.run_streamed(
            writer_agent,
            input,
        )
        update_messages = [
            "Thinking about report...",
            "Planning report structure...",
            "Writing outline...",
            "Creating sections...",
            "Cleaning up formatting...",
            "Finalizing report...",
            "Finishing report...",
        ]

        last_update = time.time()
        next_message = 0
        async for _ in result.stream_events():
            if time.time() - last_update > 5 and next_message < len(update_messages):
                self.printer.update_item("writing", update_messages[next_message])
                next_message += 1
                last_update = time.time()

        self.printer.mark_item_done("writing")
        return result.final_output_as(ReportData)



class Printer:
    def __init__(self, console: Console):
        self.live = Live(console=console)
        self.items: dict[str, tuple[str, bool]] = {}
        self.hide_done_ids: set[str] = set()
        self.live.start()

    def end(self) -> None:
        self.live.stop()

    def hide_done_checkmark(self, item_id: str) -> None:
        self.hide_done_ids.add(item_id)

    def update_item(
        self, item_id: str, content: str, is_done: bool = False, hide_checkmark: bool = False
    ) -> None:
        self.items[item_id] = (content, is_done)
        if hide_checkmark:
            self.hide_done_ids.add(item_id)
        self.flush()

    def mark_item_done(self, item_id: str) -> None:
        self.items[item_id] = (self.items[item_id][0], True)
        self.flush()

    def flush(self) -> None:
        renderables: list[Any] = []
        for item_id, (content, is_done) in self.items.items():
            if is_done:
                prefix = "✅ " if item_id not in self.hide_done_ids else ""
                renderables.append(prefix + content)
            else:
                renderables.append(Spinner("dots", text=content))
        self.live.update(Group(*renderables))



async def main() -> None:
    query = input("What would you like to research? ")
    await ResearchManager().run(query)


if __name__ == "__main__":
    asyncio.run(main())