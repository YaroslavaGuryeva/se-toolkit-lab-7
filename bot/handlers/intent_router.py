"""Intent router for natural language queries.

Uses LLM with tool calling to route user queries to the appropriate API endpoints.
"""
import json
import sys
from typing import Any

from services.lms_api import get_lms_client
from services.llm_client import get_llm_client


# System prompt for the LLM
SYSTEM_PROMPT = """You are an assistant for a Learning Management System (LMS).
Your job is to help users query information about labs, tasks, learners, and scores.

You have access to tools that fetch data from the LMS backend.
When a user asks a question, use the appropriate tool(s) to get the data, then summarize the results.

IMPORTANT: 
- Always call tools directly. Do NOT say "I will call a tool" - just call it.
- For comparisons (e.g., "which lab has the lowest pass rate"), you MUST call get_pass_rates for EACH lab before answering.
- After getting all data, compare and provide a specific answer with numbers.

Available tools:
1. `get_items` - Get list of all labs (use first to discover lab IDs like lab-01, lab-02, etc.)
2. `get_pass_rates` - Get per-task scores for a lab (requires lab parameter)
3. `get_scores` - Get score distribution for a lab
4. `get_completion_rate` - Get completion percentage for a lab
5. `get_top_learners` - Get top students for a lab
6. `get_groups` - Get group performance for a lab
7. `get_timeline` - Get submission timeline for a lab
8. `get_learners` - Get all enrolled students
9. `trigger_sync` - Refresh data from autochecker

Always call tools when you need data. Do not make up numbers or facts.
"""

# Tool schemas for all 9 backend endpoints
TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "get_items",
            "description": "Get list of all labs and tasks. Use this to discover what labs are available.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_learners",
            "description": "Get list of all enrolled learners. Use this to answer questions about student enrollment.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_scores",
            "description": "Get score distribution (4 buckets) for a specific lab.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g., 'lab-01', 'lab-04'"},
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_pass_rates",
            "description": "Get per-task average scores and attempt counts for a specific lab.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g., 'lab-01', 'lab-04'"},
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_timeline",
            "description": "Get submission timeline (submissions per day) for a specific lab.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g., 'lab-01', 'lab-04'"},
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_groups",
            "description": "Get per-group performance and student counts for a specific lab.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g., 'lab-01', 'lab-04'"},
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_learners",
            "description": "Get top N learners by score for a specific lab.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g., 'lab-01', 'lab-04'"},
                    "limit": {"type": "integer", "description": "Number of top learners to return (default: 5)"},
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_completion_rate",
            "description": "Get completion rate percentage for a specific lab.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g., 'lab-01', 'lab-04'"},
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "trigger_sync",
            "description": "Trigger ETL sync to refresh data from autochecker. Use when user asks to update or sync data.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]


def _debug_log(message: str) -> None:
    """Print debug message to stderr (visible in --test mode)."""
    print(f"[tool] {message}", file=sys.stderr)


def _execute_tool(name: str, arguments: dict[str, Any]) -> Any:
    """Execute a tool by calling the appropriate LMS API method.
    
    Args:
        name: Tool name (matches LMSAPIClient method name)
        arguments: Tool arguments
        
    Returns:
        Tool result or error message
    """
    client = get_lms_client()
    
    # Map tool names to client methods
    method_map = {
        'get_items': lambda: client.get_items(),
        'get_learners': lambda: client.get_learners(),
        'get_scores': lambda: client.get_scores(arguments.get('lab', '')),
        'get_pass_rates': lambda: client.get_pass_rates(arguments.get('lab', '')),
        'get_timeline': lambda: client.get_timeline(arguments.get('lab', '')),
        'get_groups': lambda: client.get_groups(arguments.get('lab', '')),
        'get_top_learners': lambda: client.get_top_learners(
            arguments.get('lab', ''), 
            arguments.get('limit', 5)
        ),
        'get_completion_rate': lambda: client.get_completion_rate(arguments.get('lab', '')),
        'trigger_sync': lambda: client.trigger_sync(),
    }
    
    method = method_map.get(name)
    if method is None:
        return f"Unknown tool: {name}"
    
    result = method()
    
    # Log result summary
    if isinstance(result, tuple) and result[0] is False:
        _debug_log(f"Error: {result[1]}")
    elif isinstance(result, list):
        _debug_log(f"Result: {len(result)} items")
    elif isinstance(result, dict):
        _debug_log(f"Result: {len(result)} keys")
    else:
        _debug_log(f"Result: {result}")
    
    return result


def _format_tool_result_for_llm(result: Any) -> str:
    """Format a tool result as a concise string for the LLM."""
    if isinstance(result, tuple) and result[0] is False:
        return f"Error: {result[1]}"
    
    # Format lists and dicts more concisely
    if isinstance(result, list):
        if len(result) == 0:
            return "No results found."
        # For pass_rates, extract key info
        if result and isinstance(result[0], dict) and 'task' in result[0]:
            items = []
            for item in result:
                task = item.get('task', 'Unknown')
                avg = item.get('avg_score', 0)
                items.append(f"{task}: {avg:.1f}%")
            return "\n".join(items)
        # For items (labs), extract lab titles
        if result and isinstance(result[0], dict) and 'type' in result[0]:
            labs = [item.get('title', '') for item in result if item.get('type') == 'lab']
            return f"Labs: {', '.join(labs)}"
        return str(result)
    
    if isinstance(result, dict):
        # For completion rate
        if 'completion_rate' in result:
            rate = result.get('completion_rate', 0)
            passed = result.get('passed', 0)
            total = result.get('total', 0)
            return f"Completion rate: {rate:.1f}% ({passed}/{total} students)"
        return str(result)
    
    return str(result)


def route(user_message: str) -> str:
    """Route a user message through the LLM tool calling loop.
    
    Args:
        user_message: The user's natural language query
        
    Returns:
        Formatted response text
    """
    llm = get_llm_client()
    
    # Initialize conversation with system prompt
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]
    
    max_iterations = 10  # Allow more iterations for multi-step queries
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        
        # Call LLM
        response = llm.chat(messages, tools=TOOL_SCHEMAS)
        
        # Check for LLM errors
        if "error" in response:
            return f"LLM error: {response['error']}"
        
        content = response.get("content", "")
        tool_calls = response.get("tool_calls", [])
        
        # If no tool calls, return the LLM's response
        if not tool_calls:
            if content:
                return content
            return "I'm not sure how to help with that. Try asking about labs, scores, learners, or groups."
        
        # Execute tool calls and collect results
        tool_results = []
        for tool_call in tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["arguments"]
            
            _debug_log(f"LLM called: {tool_name}({tool_args})")
            
            result = _execute_tool(tool_name, tool_args)
            formatted_result = _format_tool_result_for_llm(result)
            
            tool_results.append({
                "tool_call_id": tool_call["id"],
                "result": result,
                "formatted": formatted_result,
            })
        
        # Feed tool results back to LLM
        _debug_log(f"Feeding {len(tool_results)} tool result(s) back to LLM")

        # Add assistant's message with tool calls (content should be empty when there are tool_calls)
        messages.append({
            "role": "assistant",
            "content": None,  # OpenAI spec: content is null when there are tool_calls
            "tool_calls": [
                {
                    "id": tc["id"],
                    "type": "function",
                    "function": {
                        "name": tc["name"],
                        "arguments": json.dumps(tc["arguments"]),
                    },
                }
                for tc in tool_calls
            ],
        })
        
        # Add tool results as separate messages
        for tr in tool_results:
            messages.append({
                "role": "tool",
                "tool_call_id": tr["tool_call_id"],
                "content": tr["formatted"],
            })
    
    # If we reach max iterations, ask LLM to summarize what we have
    messages.append({
        "role": "system",
        "content": "You have received data from the tools. Please summarize the results and provide a clear, direct answer to the user's original question. Use the actual data you received.",
    })
    
    final_response = llm.chat(messages)
    return final_response.get("content", "I was unable to process your request.")
