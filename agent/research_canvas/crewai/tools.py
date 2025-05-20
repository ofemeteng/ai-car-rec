"""
Tools
"""
import os
import json
import logging
from typing_extensions import Dict, Any, List, cast
from tavily import TavilyClient
from copilotkit.crewai import copilotkit_emit_state, copilotkit_predict_state, copilotkit_stream
from litellm import completion
from litellm.types.utils import Message as LiteLLMMessage, ChatCompletionMessageToolCall


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


HITL_TOOLS = []

tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
api_key = os.getenv("OPENROUTER_API_KEY")
if api_key is None:
    raise ValueError("OPENROUTER_API_KEY environment variable not set.")

# Custom JSON encoder to handle Message objects
class MessageEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, LiteLLMMessage) or (hasattr(obj, "__class__") and obj.__class__.__name__ == "Message"):
            # Convert Message object to a serializable dictionary
            return {
                'role': getattr(obj, 'role', ''),
                'content': getattr(obj, 'content', ''),
                'tool_calls': getattr(obj, 'tool_calls', []),
                'tool_call_id': getattr(obj, 'tool_call_id', None)
            }
        elif isinstance(obj, ChatCompletionMessageToolCall) or (hasattr(obj, "__class__") and obj.__class__.__name__ == "ChatCompletionMessageToolCall"):
            # Convert ChatCompletionMessageToolCall to a serializable dictionary
            return {
                'id': getattr(obj, 'id', ''),
                'type': getattr(obj, 'type', ''),
                'function': {
                    'name': getattr(obj.function, 'name', '') if hasattr(obj, 'function') else '',
                    'arguments': getattr(obj.function, 'arguments', '') if hasattr(obj, 'function') else ''
                }
            }
        return super().default(obj)

# Helper function to prepare state for JSON serialization
def prepare_state_for_serialization(state):
    """
    Recursively convert non-serializable objects in state to serializable dictionaries.
    """
    if isinstance(state, dict):
        # Handle dictionary
        result = {}
        for key, value in state.items():
            result[key] = prepare_state_for_serialization(value)
        return result
    elif isinstance(state, list):
        # Handle list
        return [prepare_state_for_serialization(item) for item in state]
    elif isinstance(state, (str, int, float, bool, type(None))):
        # Base primitive types
        return state
    elif isinstance(state, LiteLLMMessage) or (hasattr(state, "__class__") and state.__class__.__name__ == "Message"):
        # Handle Message objects
        return {
            'role': getattr(state, 'role', ''),
            'content': getattr(state, 'content', ''),
            'tool_calls': prepare_state_for_serialization(getattr(state, 'tool_calls', [])),
            'tool_call_id': getattr(state, 'tool_call_id', None)
        }
    elif isinstance(state, ChatCompletionMessageToolCall) or (hasattr(state, "__class__") and state.__class__.__name__ == "ChatCompletionMessageToolCall"):
        # Handle ChatCompletionMessageToolCall objects
        function_data = {}
        if hasattr(state, 'function'):
            function_data = {
                'name': getattr(state.function, 'name', ''),
                'arguments': getattr(state.function, 'arguments', '')
            }
        
        return {
            'id': getattr(state, 'id', ''),
            'type': getattr(state, 'type', ''),
            'function': function_data
        }
    else:
        # Try to convert other objects to dict if possible
        try:
            # Try to convert to dict using __dict__
            if hasattr(state, '__dict__'):
                return prepare_state_for_serialization(state.__dict__)
            # Try to use model_dump for pydantic models
            elif hasattr(state, 'model_dump'):
                return prepare_state_for_serialization(state.model_dump())
            # If object has a to_dict method
            elif hasattr(state, 'to_dict') and callable(getattr(state, 'to_dict')):
                return prepare_state_for_serialization(state.to_dict())
            # Last resort: try to convert using vars()
            else:
                return prepare_state_for_serialization(vars(state))
        except:
            # If all else fails, convert to string
            return str(state)

async def perform_tool_calls(state: Dict[str, Any]):
    """
    Perform tool calls on the state.
    """
    if len(state["messages"]) == 0:
        return False
    message = state["messages"][-1]

    if not message.get("tool_calls"):
        return False

    tool_call = message["tool_calls"][0]
    tool_call_id = tool_call["id"]
    tool_call_name = tool_call["function"]["name"]
    tool_call_args = json.loads(tool_call["function"]["arguments"])

    if tool_call_name in HITL_TOOLS:
        return False

    if tool_call_name == "Search":
        queries = tool_call_args.get("queries", [])
        await perform_search(state, queries, tool_call_id)

    elif tool_call_name == "ExtractResources":
        state["report"] = tool_call_args.get("recommendations", "")
        state["messages"].append({
            "role": "tool",
            "content": "Resources extracted.",
            "tool_call_id": tool_call_id
        })

    elif tool_call_name == "DeepDiveReview":
        state["report"] = tool_call_args.get("car_name", "")
        state["messages"].append({
            "role": "tool",
            "content": "Deep Dive Report written.",
            "tool_call_id": tool_call_id
        })

    return True

async def perform_search(state: Dict[str, Any], queries: List[str], tool_call_id: str):
    """
    Perform a search.
    """
    # state["resources"] = state.get("resources", [])
    # state["logs"] = state.get("logs", [])

    state["recommendations"] = state.get("recommendations", [])
    state["logs"] = state.get("logs", [])

    for query in queries:
        state["logs"].append({
            "message": f"Search for {query}",
            "done": False
        })

    # Use the prepared state for serialization
    serializable_state = prepare_state_for_serialization(state)
    await copilotkit_emit_state(serializable_state)

    search_results = []

    for i, query in enumerate(queries):
        response = tavily_client.search(query)
        search_results.append(response)
        state["logs"][i]["done"] = True
        # Use the prepared state for serialization
        serializable_state = prepare_state_for_serialization(state)
        await copilotkit_emit_state(serializable_state)

    await copilotkit_predict_state(
        {
            "recommendations": {
                "tool_name": "ExtractResources",
                "tool_argument": "recommendations",
            },
        }
    )

    response = await copilotkit_stream(
        completion(
            # model="openai/deepseek/deepseek-chat",
            model="openai/deepseek/deepseek-chat-v3-0324",
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            messages=[
                {
                    "role": "system", 
                    "content": "You need to extract the 3-5 most relevant recommendations from the following search results."
                },
                *state["messages"],
                {
                    "role": "tool",
                    "content": f"Performed search: {search_results}",
                    "tool_call_id": tool_call_id
                }
            ],
            tools=[EXTRACT_RESOURCES_TOOL],
            tool_choice="required",
            parallel_tool_calls=False,
            stream=True
        )
    )

    state["logs"] = []
    # Use the prepared state for serialization
    serializable_state = prepare_state_for_serialization(state)
    await copilotkit_emit_state(serializable_state)

    message = cast(Any, response).choices[0]["message"]
    recommendations = json.loads(message["tool_calls"][0]["function"]["arguments"])["recommendations"]

    state["recommendations"].extend(recommendations)

    state["messages"].append({
        "role": "tool",
        "content": f"Added the following recommendations: {recommendations}",
        "tool_call_id": tool_call_id
    })

# Tool definitions (EXTRACT_RESOURCES_TOOL, SEARCH_TOOL, etc.)
EXTRACT_RESOURCES_TOOL = {
    "type": "function",
    "function": {
        "name": "ExtractResources",
        "description": "Extract the 3-5 most relevant car information and create recommendations from the search result. Respond ONLY with the valid JSON for the tool call arguments. MAKE SURE IT IS in the expected tool_calls structure below.",
        "parameters": {
            "type": "object",
            "properties": {
                "recommendations": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "car": {"type": "string", "description": "The name of the car"},
                            "tagline": {"type": "string", "description": "The tagline of the car recommendation"},
                            "content": {"type": "string", "description": "A short content/description of the car recommendation"}
                        },
                        "required": ["car", "tagline", "content"]
                    },
                    "description": "The list of recommendations. Each recommendation must include a car name, a tagline, and content."
                },
            },
            "required": ["recommendations"]
        },
    },
}

SEARCH_TOOL = {
    "type": "function",
    "function": {
        "name": "Search",
        "description": "Provide a list of one or more search queries to find good resources for the research.",
        "parameters": {
            "type": "object",
            "properties": {"queries": {"type": "array", "items": {"type": "string"}, "description": "The list of search queries",},},
            "required": ["queries"],
        },
    },
}

# pristine
# DEEP_DIVE_REVIEW_TOOL = {
#     "type": "function",
#     "function": {
#         "name": "DeepDiveReview",
#         "description": "Performs a detailed search and writes an in-depth review for a specifically selected car. Use this tool when the user explicitly asks for more details, a review, deep dive or wants to 'know more' about one particular car from the recommendations.",
#         "parameters": {
#             "type": "object",
#             "properties": {
#                 "car_name": {
#                     "type": "string",
#                     "description": "The full name of the car for which a detailed review is requested (e.g., 'Tesla Model Y'). This should match a car name from previous recommendations."
#                 },
#             },
#             "required": ["car_name"],
#         },
#     },
# }

DEEP_DIVE_REVIEW_TOOL = {
    "type": "function",
    "function": {
        "name": "DeepDiveReview",
        "description": "Write an indepth research report on a specific selected car. Use this tool when the user explicitly asks for more details, a review, deep dive or wants to 'know more' about one particular car from the recommendations.",
        "parameters": {
            "type": "object",
            "properties": {
                "car_name": {
                    "type": "string",
                    "description": "The full name of the car for which a detailed review is requested (e.g., 'Tesla Model Y'). This should match a car name from previous recommendations."
                },
            },
            "required": ["car_name"],
        },
    },
}


