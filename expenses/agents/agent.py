import json

from agent_state import AgentState
from langgraph.graph import END, StateGraph
from llm_manager import llm_manager
from tools import TOOLS, ExpenseTools


class ExpenseAgent:
    def __init__(self, token: str):
        self.tools = ExpenseTools(token)
        self.graph = self.build_graph()

    # select best model
    def _select_model(self, state: AgentState) -> AgentState:
        # static for now: default to claude haiku model
        state["selected_model"] = "claude"
        return state

    # process with model
    def _process(self, state: AgentState) -> AgentState:

        state["step_count"] += 1

        if state["step_count"] > state["max_steps"]:
            state["last_error"] = "Max steps exceeded"
            return state

        # get model
        model = llm_manager.get_model(state["selected_model"])

        # Bind tools to model
        model_with_tools = model.bind_tools(TOOLS, tool_choice="auto")

        # Call model
        response = model_with_tools.invoke(state["messages"])

        # Add response to messages
        state["messages"].append(
            {
                "role": "assistant",
                "content": response.content if hasattr(response, "content") else str(response),
            }
        )

        return state

    # condition to execute tools
    def _should_execute_tools(self, state: AgentState) -> bool:
        last_message = state["messages"][-1]
        return (
            hasattr(last_message.get("content"), "tool_calls")
            or "tool_calls" in str(last_message.get("content", "")).lower()
        )

    def _execute_tools(self, state: AgentState) -> AgentState:

        last_message = state["messages"][-1]

        # Extract tool calls
        tool_calls = getattr(last_message.get("content"), "tool_calls", [])

        for tool_call in tool_calls:
            tool_name = tool_call.name
            tool_input = tool_call.input

            try:
                if tool_name == "create_expense":
                    result = self.tools.create_expense(**tool_input)
                elif tool_name == "get_expense":
                    result = self.tools.get_expenses(**tool_input)
                elif tool_name == "delete_expense":
                    result = self.tools.delete_expense(**tool_input)
                else:
                    result = {"error": f"Unknown tool: {tool_name}"}

                state["messages"].append(
                    {"role": "user", "content": f"Tool '{tool_name} result: {json.dumps(result)}"}
                )
            except Exception as e:
                state["last_error"] = str(e)
                return
        return state

    # Agent should continue or not.
    def _should_continue(self, state: AgentState) -> str:
        if state["last_error"]:
            return "error"
        if state["step_count"] >= state["max_steps"]:
            return "done"
        return "continue"

    def _handl_error(self, state: AgentState) -> AgentState:
        print(f"❌ Error: {state['last_error']}")

        # Add error message to conversation

        state["messages"].append(
            {
                "role": "system",
                "content": f"Error occurred: {state['last_error']}. Please try again or provide more information.",
            }
        )

        return state

    def build_graph(self) -> StateGraph:
        graph = StateGraph(AgentState)

        graph.add_node("select_model", self._select_model)
        graph.add_node("process", self._process)
        graph.add_node("execute_tools", self._execute_tools)
        graph.add_node("error_handle", self._handl_error)

        # Add edges(workflow)
        graph.add_edge("select_edge", "process")
        graph.add_conditional_edges(
            "process", self._should_execute_tools, {True: "execute_tools", False: END}
        )
        graph.add_conditional_edges(
            "execute_tools",
            self._should_continue,
            {"continue": "process", "error": "error_handle", "done": END},
        )

        graph.add_edge("error_handler", END)

        # set entry points
        graph.set_entry_point("select_model")

        return graph.compile()
