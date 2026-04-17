
"""Backward-compatible exports for tests and existing imports."""
 

from agent.graph_builder import (
    SYSTEM_PROMPT,
    agent_node,
    build_graph,
    llm,
    llm_with_tools,
    tools_list,
)
 
# Keep the old module-level `graph` symbol for existing test code.
graph = build_graph()
 
if __name__ == "__main__":
    from agent.cli import run_cli
    run_cli()
