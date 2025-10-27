import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.chat_models import ChatOllama
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator

load_dotenv()

# Define the state for our graph
class AgentState(TypedDict):
    query: str
    response: str
    is_blocked: bool

# Node 1: Keyword Checker
def keyword_checker(state):
    """Checks for blocked keywords in the query."""
    blocked_keywords = ["transfer funds", "withdraw money"]
    query = state["query"]
    is_blocked = any(keyword in query.lower() for keyword in blocked_keywords)
    return {"is_blocked": is_blocked, "query": query}

# Node 2: Basic Responder
def basic_responder(state):
    """Generates a response using a language model."""
    query = state["query"]
    
    model_provider = os.getenv("MODEL_PROVIDER", "openai").lower()

    if model_provider == "ollama":
        model_name = os.getenv("OLLAMA_MODEL", "llama2")
        llm = ChatOllama(model=model_name)
    else:
        llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
    response = llm.invoke(f"You are a helpful financial assistant. Answer the following query: {query}")
    return {"response": response.content}

# Node 3: Blocker
def blocker(state):
    """Blocks the request and provides a canned response."""
    return {"response": "Sorry, I cannot process this request."}

# Conditional Edge
def should_block(state):
    """Determines whether to block the request or not."""
    if state["is_blocked"]:
        return "block"
    else:
        return "respond"

# Define the graph
workflow = StateGraph(AgentState)
workflow.add_node("checker", keyword_checker)
workflow.add_node("responder", basic_responder)
workflow.add_node("blocker", blocker)

# Set the entry point
workflow.set_entry_point("checker")

# Add the conditional edge
workflow.add_conditional_edges(
    "checker",
    should_block,
    {
        "block": "blocker",
        "respond": "responder",
    },
)

# Add edges to the end
workflow.add_edge("responder", END)
workflow.add_edge("blocker", END)

# Compile the graph
app_graph = workflow.compile()

def get_agent_response(query: str):
    """Runs the agent graph and returns the final response."""
    inputs = {"query": query}
    final_state = app_graph.invoke(inputs)
    return final_state["response"]
