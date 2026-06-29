
# 06/28

1. Added expense tracker tools 
    - add expense
    - get expense
    - delete expense

2. Added Ruff for format
    - ruff check . --fix      # Lint + auto-fix
    - ruff format .           # Format code

-----------------------------------------------------------------------------------------

# 06/28 after session

1. Build Langraph agent
2. Define state graph
    - select model (node)
    - process with model( bind tools)
    - execute tools
    - should execute tools
    - should continue (validate if max steps reached).
3. compile graph - graph.compile()
