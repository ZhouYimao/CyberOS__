from langchain_core.messages import AIMessage

from langgraph.prebuilt import ToolNode


def get_weather(location: str) -> str:
    """Call to get the current weather."""
    if location.lower() in ["sf", "san francisco"]:
        return "It's 60 degrees and foggy."
    else:
        return "It's 90 degrees and sunny."


def get_coolest_cities() -> str:
    """Get a list of coolest cities"""
    return "nyc, sf"

# Create the tool node with the tools
tools = [get_weather, get_coolest_cities]
tool_node = ToolNode(tools)


message_with_multiple_tool_calls = AIMessage(
    content="",
    tool_calls=[
        {
            "name": "get_coolest_cities",
            "args": {},
            "id": "tool_call_id_1",
            "type": "tool_call",
        },
        {
            "name": "get_weather",
            "args": {"location": "sf"},
            "id": "tool_call_id_2",
            "type": "tool_call",
        },
    ],
)

print(tool_node.invoke({"messages": [message_with_multiple_tool_calls]}))

