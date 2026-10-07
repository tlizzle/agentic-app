# The ticket service is an MCP server in this repo, launched over stdio

Tickets live behind a small MCP server in the repo that ADK spawns as a subprocess over stdio, storing Tickets in a JSON file. Reusing a public MCP server (filesystem, GitHub) was rejected because it would not show the Approval flow on a domain action, and a Python function tool was rejected because the point is to show MCP as the integration boundary. Stdio over HTTP keeps the demo to one command with nothing else to start.
