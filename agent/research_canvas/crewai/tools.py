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

# Custom JSON encoder
class MessageEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, LiteLLMMessage) or (hasattr(obj, "__class__") and obj.__class__.__name__ == "Message"):
            return {
                'role': getattr(obj, 'role', ''),
                'content': getattr(obj, 'content', ''),
                'tool_calls': getattr(obj, 'tool_calls', []),
                'tool_call_id': getattr(obj, 'tool_call_id', None)
            }
        elif isinstance(obj, ChatCompletionMessageToolCall) or (hasattr(obj, "__class__") and obj.__class__.__name__ == "ChatCompletionMessageToolCall"):
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
    if isinstance(state, dict):
        result = {}
        for key, value in state.items():
            result[key] = prepare_state_for_serialization(value)
        return result
    elif isinstance(state, list):
        return [prepare_state_for_serialization(item) for item in state]
    elif isinstance(state, (str, int, float, bool, type(None))):
        return state
    elif isinstance(state, LiteLLMMessage) or (hasattr(state, "__class__") and state.__class__.__name__ == "Message"):
        return {
            'role': getattr(state, 'role', ''),
            'content': getattr(state, 'content', ''),
            'tool_calls': prepare_state_for_serialization(getattr(state, 'tool_calls', [])),
            'tool_call_id': getattr(state, 'tool_call_id', None)
        }
    elif isinstance(state, ChatCompletionMessageToolCall) or (hasattr(state, "__class__") and state.__class__.__name__ == "ChatCompletionMessageToolCall"):
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
        try:
            if hasattr(state, '__dict__'):
                return prepare_state_for_serialization(state.__dict__)
            elif hasattr(state, 'model_dump'):
                return prepare_state_for_serialization(state.model_dump())
            elif hasattr(state, 'to_dict') and callable(getattr(state, 'to_dict')):
                return prepare_state_for_serialization(state.to_dict())
            else:
                return prepare_state_for_serialization(vars(state))
        except:
            return str(state)

async def perform_tool_calls(state: Dict[str, Any]):
    if len(state["messages"]) == 0:
        return False
    
    last_message_obj = state["messages"][-1]
    if isinstance(last_message_obj, LiteLLMMessage) or (hasattr(last_message_obj, "__class__") and last_message_obj.__class__.__name__ == "Message"):
         message = {
            'role': getattr(last_message_obj, 'role', ''),
            'content': getattr(last_message_obj, 'content', ''),
            'tool_calls': prepare_state_for_serialization(getattr(last_message_obj, 'tool_calls', [])),
            'tool_call_id': getattr(last_message_obj, 'tool_call_id', None)
        }
    elif isinstance(last_message_obj, dict):
        message = last_message_obj
    else:
        logger.error(f"Unexpected message type in state['messages'][-1]: {type(last_message_obj)}")
        return False

    if not message.get("tool_calls"):
        return False

    tool_call = message["tool_calls"][0]
    tool_call_id = tool_call["id"]
    tool_call_name = tool_call["function"]["name"]
    raw_arguments = tool_call["function"]["arguments"]
    logger.info(f"Raw arguments for tool {tool_call_name}: {raw_arguments}")

    try:
        tool_call_args = json.loads(raw_arguments)
    except json.JSONDecodeError as e:
        logger.error(f"JSONDecodeError for tool {tool_call_name} with arguments: {raw_arguments}. Error: {e}")
        try:
            obj, end = json.JSONDecoder().raw_decode(raw_arguments)
            tool_call_args = obj
            logger.info(f"Successfully parsed arguments using raw_decode. Extracted: {tool_call_args}")
            if raw_arguments[end:].strip():
                 logger.warning(f"Extra data found after JSON: '{raw_arguments[end:].strip()}'")
        except json.JSONDecodeError as e2:
            logger.error(f"raw_decode also failed for tool {tool_call_name}. Arguments remain unparseable: {raw_arguments}. Error: {e2}")
            state["messages"].append({
                "role": "tool",
                "content": f"Error: Could not parse arguments for tool {tool_call_name}. Arguments received: {raw_arguments}. Error: {e2}",
                "tool_call_id": tool_call_id
            })
            return True 

    if tool_call_name in HITL_TOOLS:
        return False

    if tool_call_name == "Search":
        queries = tool_call_args.get("queries", [])
        await perform_search(state, queries, tool_call_id)
    elif tool_call_name == "DeepDiveReview": # New tool
        car_name = tool_call_args.get("car_name")
        if car_name:
            await perform_deep_dive_review(state, car_name, tool_call_id)
        else:
            logger.error("DeepDiveReview called without car_name.")
            state["messages"].append({
                "role": "tool",
                "content": "Error: DeepDiveReview tool was called without specifying a car_name.",
                "tool_call_id": tool_call_id
            })
    # elif tool_call_name == "WriteReport":
    #     state["report"] = tool_call_args.get("report", "")
    #     state["messages"].append({ "role": "tool", "content": "Report written.", "tool_call_id": tool_call_id })

    return True

async def perform_search(state: Dict[str, Any], queries: List[str], tool_call_id: str):
    state["recommendations"] = state.get("recommendations", [])
    state["logs"] = state.get("logs", [])

    for query in queries:
        state["logs"].append({"message": f"Search for {query}", "done": False})
    
    serializable_state = prepare_state_for_serialization(state)
    await copilotkit_emit_state(serializable_state)

    search_results = []
    for i, query in enumerate(queries):
        response = tavily_client.search(query)
        search_results.append(response)
        state["logs"][i]["done"] = True
        serializable_state_update = prepare_state_for_serialization(state) # MODIFICATION: Renamed to avoid conflict
        await copilotkit_emit_state(serializable_state_update)

    await copilotkit_predict_state({
        "recommendations": { "tool_name": "ExtractResources", "tool_argument": "recommendations" },
    })
    
    serializable_messages_for_llm = prepare_state_for_serialization(state["messages"])

    llm_response_object = await copilotkit_stream( # Renamed from response_stream to llm_response_object
        completion(
            model="openai/deepseek/deepseek-chat-v3-0324",
            # model="openai/gpt-4o",
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            messages=[
                {"role": "system", "content": "You need to extract the 3-5 most relevant recommendations from the following search results as related to the research question. Respond ONLY with the valid JSON for the tool call arguments, conforming to the tool's schema."},
                *serializable_messages_for_llm,
                {"role": "tool", "content": f"Performed search: {json.dumps(search_results)}", "tool_call_id": tool_call_id}
            ],
            tools=[EXTRACT_RESOURCES_TOOL],
            tool_choice="required",
            parallel_tool_calls=False,
            stream=True # stream=True means litellm will internally handle the stream and provide an assembled ModelResponse
        )
    )

    state["logs"] = [] # Clear logs after search and before emitting final state for this step
    await copilotkit_emit_state(prepare_state_for_serialization(state)) # Emit state before processing recommendations

    recommendations = [] # Default to empty list
    extracted_tool_call_id = tool_call_id # Fallback to original search tool_call_id

    if not (llm_response_object and \
            hasattr(llm_response_object, 'choices') and llm_response_object.choices and \
            hasattr(llm_response_object.choices[0], 'message') and llm_response_object.choices[0].message and \
            hasattr(llm_response_object.choices[0].message, 'tool_calls') and llm_response_object.choices[0].message.tool_calls and \
            len(llm_response_object.choices[0].message.tool_calls) > 0 and \
            hasattr(llm_response_object.choices[0].message.tool_calls[0], 'function') and llm_response_object.choices[0].message.tool_calls[0].function):
        logger.error("LLM response (ExtractResources) did not contain expected tool_calls structure.")
        state["messages"].append({
            "role": "tool",
            "content": "Error: LLM response did not adhere to tool call format for extracting recommendations.",
            "tool_call_id": tool_call_id 
        })
    else:
        extracted_tool_call = llm_response_object.choices[0].message.tool_calls[0]
        arguments_str = extracted_tool_call.function.arguments
        extracted_tool_call_id = extracted_tool_call.id or tool_call_id # Use the ID from the extracted tool call

        logger.info(f"Arguments string from LLM for ExtractResources: '{arguments_str}'")
        try:
            parsed_args = json.loads(arguments_str)
            recommendations = parsed_args.get("recommendations", [])
        except json.JSONDecodeError as e:
            logger.error(f"JSONDecodeError while parsing ExtractResources arguments: {e}. Arguments: '{arguments_str}'")
            try:
                obj, end = json.JSONDecoder().raw_decode(arguments_str)
                parsed_args = obj
                recommendations = parsed_args.get("recommendations", [])
                logger.info(f"Successfully parsed arguments using raw_decode. Extracted: {parsed_args}")
                if arguments_str[end:].strip():
                    logger.warning(f"Extra data found after JSON for ExtractResources: '{arguments_str[end:].strip()}'")
            except json.JSONDecodeError as e2:
                logger.error(f"raw_decode also failed for ExtractResources. Arguments: '{arguments_str}'. Error: {e2}")
                # Error message already added to state["messages"] by the calling perform_tool_calls if initial parsing fails there.
                # If we reach here, it means parsing the specific 'ExtractResources' arguments failed.
                state["messages"].append({
                    "role": "tool",
                    "content": f"Error: Could not parse recommendations from LLM response. Arguments received: {arguments_str}. Error: {e2}",
                    "tool_call_id": extracted_tool_call_id
                })
                # recommendations will remain an empty list

    state["recommendations"].extend(recommendations)
    state["messages"].append({
        "role": "tool",
        "content": f"Added the following resources: {json.dumps(recommendations)}" if recommendations else "No new recommendations were extracted or an error occurred during extraction.",
        "tool_call_id": extracted_tool_call_id
    })

# --- New Deep Dive Tool Implementation ---
async def perform_deep_dive_review(state: Dict[str, Any], car_name: str, tool_call_id: str):
    logger.info(f"Performing deep dive review for: {car_name}")
    state["logs"] = state.get("logs", []) # Clear previous logs or use a different log key
    # state["logs"].append({"message": f"Starting deep dive for {car_name}...", "done": False})
    state["current_detailed_review"] = None # Clear previous review
    await copilotkit_emit_state(prepare_state_for_serialization(state))

    detailed_search_queries = [
        f"in-depth review of {car_name} performance and driving experience",
        f"{car_name} interior features, comfort, and technology",
        f"{car_name} safety ratings and features",
        f"{car_name} reliability and owner satisfaction",
        f"common pros and cons of {car_name}"
    ]
    
    search_results_texts = []
    for i, query in enumerate(detailed_search_queries):
        log_message = f"Deep dive search: {query}"
        state["logs"].append({"message": log_message, "done": False})
        await copilotkit_emit_state(prepare_state_for_serialization(state))
        try:
            response = tavily_client.search(query, search_depth="advanced", max_results=2) # Tavily returns dict
            # Extract content from results
            for res in response.get("results", []):
                search_results_texts.append(res.get("content", ""))
            
            for log_entry in state["logs"]: # Update specific log
                if log_entry["message"] == log_message and not log_entry["done"]:
                    log_entry["done"] = True
                    break
        except Exception as e:
            logger.error(f"Error during Tavily deep dive search for query '{query}': {e}")
            for log_entry in state["logs"]:
                 if log_entry["message"] == log_message and not log_entry["done"]:
                    log_entry["message"] = f"Error during deep dive search for '{query}': {str(e)[:100]}"
                    log_entry["done"] = True
                    break
        await copilotkit_emit_state(prepare_state_for_serialization(state))

    review_text = f"Could not find sufficient information to write a detailed review for {car_name} at this time."
    if search_results_texts:
        compiled_info = "\n\n---\n\n".join(search_results_texts)
        log_message_synth = f"Synthesizing detailed review for {car_name}..."
        state["logs"].append({"message": log_message_synth, "done": False})
        await copilotkit_emit_state(prepare_state_for_serialization(state))
        try:
            review_completion = await completion( # Not using copilotkit_stream as we need full response
                model="openai/gpt-4o", 
                base_url="https://openrouter.ai/api/v1", api_key=api_key,
                messages=[
                    {"role": "system", "content": f"You are an expert automotive journalist. Based ONLY on the following compiled information, write a comprehensive, objective, and well-structured detailed review for the {car_name}. Cover aspects like performance, interior, technology, safety, reliability, pros, and cons. If information for an aspect is missing, clearly state that. Do not invent information. Respond only with the review text itself, formatted nicely for readability (e.g., using markdown paragraphs)."},
                    {"role": "user", "content": f"Compile information for {car_name}:\n\n{compiled_info}"}
                ],
                num_retries=1
            )
            if review_completion.choices and review_completion.choices[0].message.content:
                review_text = review_completion.choices[0].message.content
            else:
                logger.error(f"LLM did not return content for {car_name} review.")
                review_text = f"Failed to generate a review for {car_name} as the LLM response was empty."

            for log_entry in state["logs"]:
                 if log_entry["message"] == log_message_synth and not log_entry["done"]:
                    log_entry["done"] = True
                    break
        except Exception as e:
            logger.error(f"Error generating detailed review for {car_name} with LLM: {e}")
            review_text = f"An error occurred while generating the detailed review for {car_name}: {str(e)[:100]}"
            for log_entry in state["logs"]:
                 if log_entry["message"] == log_message_synth and not log_entry["done"]:
                    log_entry["message"] = f"Error synthesizing review for {car_name}: {str(e)[:100]}"
                    log_entry["done"] = True
                    break
        await copilotkit_emit_state(prepare_state_for_serialization(state))
    
    state["current_detailed_review"] = {"car_name": car_name, "review_text": review_text}
    state["logs"] = [] 
    await copilotkit_emit_state(prepare_state_for_serialization(state))

    state["messages"].append({
        "role": "tool",
        "content": f"Generated detailed review for {car_name}. You can now view it or ask further questions.",
        "tool_call_id": tool_call_id
    })
    logger.info(f"Finished deep dive review for {car_name}")

# Tool definitions (EXTRACT_RESOURCES_TOOL, SEARCH_TOOL, etc.)
EXTRACT_RESOURCES_TOOL = {
    "type": "function",
    "function": {
        "name": "ExtractResources",
        "description": "Extract the 3-5 most relevant car recommendations from a search result. Respond ONLY with the valid JSON for the tool call arguments.",
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

DEEP_DIVE_REVIEW_TOOL = {
    "type": "function",
    "function": {
        "name": "DeepDiveReview",
        "description": "Performs a detailed search and writes an in-depth review for a specifically selected car. Use this tool when the user explicitly asks for more details, a review, deep dive or wants to 'know more' about one particular car from the recommendations.",
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