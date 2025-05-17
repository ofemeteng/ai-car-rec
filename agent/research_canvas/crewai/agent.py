"""
This is the main entry point for the CrewAI agent.
"""

import os
from typing_extensions import Dict, Any, cast
import litellm
from crewai.flow.flow import Flow, start, router, listen
from litellm import completion
from copilotkit.crewai import copilotkit_stream, copilotkit_predict_state
from research_canvas.crewai.download import download_resources, get_resources
from research_canvas.crewai.delete import maybe_perform_delete
from research_canvas.crewai.prompt import format_prompt
from research_canvas.crewai.tools import (
    SEARCH_TOOL,
    DEEP_DIVE_REVIEW_TOOL,
    perform_tool_calls
)
from litellm.exceptions import APIConnectionError

api_key = os.getenv("OPENROUTER_API_KEY")
if api_key is None:
    raise ValueError("OPENROUTER_API_KEY environment variable not set.")

class ResearchCanvasFlow(Flow[Dict[str, Any]]):
    """
    Research Canvas CrewAI Flow
    """

    @start()
    @listen("route_follow_up")
    async def start(self):
        """
        Download any pending assets that are needed for the research.
        """
        self.state["resources"] = self.state.get("resources", [])
        self.state["research_question"] = self.state.get("research_question", "")
        self.state["car_name"] = self.state.get("car_name", "")
        self.state["report"] = self.state.get("report", "")

        await download_resources(self.state)

        # If the user requested deletion, perform it
        maybe_perform_delete(self.state)



    @router(start)
    async def chat(self):
        """
        Listen for the download event.
        """
        resources = get_resources(self.state)
        prompt = format_prompt(
            self.state["research_question"],
            self.state["car_name"],
            self.state["report"],
            resources
        )

        await copilotkit_predict_state(
          {
            "report": {
              "tool_name": "DEEP_DIVE_REVIEW_TOOL",
              "tool_argument": "car_name",
            },
          }
        )

        try:
            litellm._turn_on_debug()

            response = await copilotkit_stream(
            completion(
                model="openai/deepseek/deepseek-chat-v3-0324",
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key,
                messages=[
                    {"role": "system", "content": prompt},
                    *self.state["messages"]
                ],
                tools=[
                    SEARCH_TOOL,
                    DEEP_DIVE_REVIEW_TOOL
                ],

                parallel_tool_calls=False,
                stream=True
                )
            )
            message = cast(Any, response).choices[0]["message"]

            self.state["messages"].append(message)

            follow_up = await perform_tool_calls(self.state)

            return "route_follow_up" if follow_up else "route_end"
        except APIConnectionError as e:
            print(f"APIConnectionError: {e}")
            self.state["messages"].append(
                {
                    "role": "assistant",
                    "content": "Sorry, I am having trouble connecting to the API. Please try again later."
                }
            )
            return "route_end"
        

    @listen("route_end")
    async def end(self):
        """
        End the flow.
        """

