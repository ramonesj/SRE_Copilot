# SRE Copilot MCP Server

Model Context Protocol (MCP) server for SRE Copilot integration with AI assistants.

## Security Boundary

⚠️ **READ-ONLY Access**: Cannot execute remediation actions. All remediation requires human approval through HITL workflow.

## Available Tools

1. **list_incidents** - List incidents with filters
2. **get_incident** - Get incident details
3. **list_evidence** - List evidence files
4. **get_risk_assessment** - Get risk assessment (READ-ONLY)
5. **list_approvals** - List approval requests
6. **get_audit_trail** - Get audit logs
7. **get_ai_summary** - Get AI summary
8. **get_ai_recommendation** - Get AI recommendations

## Installation

```bash
cd mcp_server
pip install -r requirements.txt
```

## Claude Desktop Setup

Copy `claude_desktop_config.json` to:
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

## Environment Variables

```env
SRE_COPILOT_API_URL=http://localhost:8000/api/v1
SRE_COPILOT_API_TIMEOUT=30.0
```

## Usage

```bash
python -m mcp_server.server
```

## License

MIT
