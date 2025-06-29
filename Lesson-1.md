...
messages = [AIMessage(content=f"So you said you were researching ocean mammals?", name="Model")]

messages.append(HumanMessage(content=f"Yes, that's right.",name="Lance"))

messages.append(AIMessage(content=f"Great, what would you like to learn about.", name="Model"))

messages.append(HumanMessage(content=f"I want to learn about the best place to see Orcas in the US.", name="Lance"))
'''
'''code
for m in messages:
    m.pretty_print()
---------------------
def _set_env(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"{var}: ")

_set_env("OPENAI_API_KEY")

We can load a chat model and invoke it with out list of messages.
We can see that the result is an `AIMessage` with specific `response_metadata`.
//code
from langchain_openai import ChatOpenAI
-----
llm_with_tools = llm.bind_tools([multiply])
If we pass an input - e.g., `"What is 2 multiplied by 3"` - we see a tool call returned. 

The tool call has specific arguments that match the input schema of our function along with the name of the function to call.
```
{'arguments': '{"a":2,"b":3}', 'name': 'multiply'}
```
tool_call = llm_with_tools.invoke([HumanMessage(content=f"What is 2 multiplied by 3", name="Lance")])
tool_call.tool_calls
list of tool calls invoked by llm
[{'name': 'multiply',
  'args': {'a': 2, 'b': 3},
  'id': 'call_lBBBNo5oYpHGRqwxNaNRbsiT',
  'type': 'tool_call'}]




llm = ChatOpenAI(model="gpt-4o")
result = llm.invoke(messages)
type(result)
>langchain_core.messages.ai.AIMessage
result.response_metadata

## Using messages as state

With these foundations in place, we can now use [`messages`](https://python.langchain.com/v0.2/docs/concepts/#messages) in our graph state.
Let's define our state, `MessagesState`, as a `TypedDict` with a single key: `messages`.
`messages` is simply a list of messages, as we defined above (e.g., `HumanMessage`, etc).

'''
from typing_extensions import TypedDict
from langchain_core.messages import AnyMessage

class MessagesState(TypedDict):
    messages: list[AnyMessage]
'''

#---------------------------

In LangGraph, nodes are typically Python functions (sync or async) where the first positional argument is the state, and (optionally), 
the second positional argument is a "config", containing optional configurable parameters (such as a thread_id).

The START Node is a special node that represents the node that sends user input to the graph. The main purpose of referencing this node 
is to determine which nodes should be called first.

'''
graph.add_edge(START, "node_a")

'''
The END Node is a special node that represents a terminal node. This node is referenced when you want to denote which edges have no actions after they are done.
'''

from langgraph.graph import END
graph.add_edge("node_a", END)
'''
LangGraph supports caching of tasks/nodes based on the input to the node. To use caching:




