"""SRE Copilot MCP Server

This MCP server provides tools for interacting with the SRE Copilot platform.
It allows AI assistants to query incidents, evidence, risk assessments, and more.

SECURITY BOUNDARY: This server provides READ-ONLY access to SRE Copilot data.
It CANNOT execute remediation actions or approve/reject incidents.
All state-changing operations must go through the HITL approval workflow.
"""
import os
import httpx
from typing import Any, Optional
from mcp.server import Server
from mcp.types import Tool, TextContent
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

# Configuration
API_BASE_URL = os.getenv("SRE_COPILOT_API_URL", "http://localhost:8000/api/v1")
API_TIMEOUT = float(os.getenv("SRE_COPILOT_API_TIMEOUT", "30.0"))

# Initialize MCP server
app = Server("sre-copilot")


class IncidentQuery(BaseModel):
    """Query parameters for incidents"""
    status: Optional[str] = None
    severity: Optional[str] = None
    service: Optional[str] = None
    skip: int = 0
    limit: int = 100


async def api_request(method: str, endpoint: str, **kwargs) -> dict:
    """Make authenticated request to SRE Copilot API"""
    async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
        url = f"{API_BASE_URL}{endpoint}"
        response = await client.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools"""
    return [
        Tool(
            name="list_incidents",
            description="List all incidents with optional filters. "
                       "Returns incident details including status, severity, and service.",
            inputSchema={
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["created", "in_progress", "approved", "rejected", "resolved"],
                        "description": "Filter by incident status"
                    },
                    "severity": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "critical"],
                        "description": "Filter by incident severity"
                    },
                    "service": {
                        "type": "string",
                        "description": "Filter by service name"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of incidents to return",
                        "default": 100
                    }
                }
            }
        ),
        Tool(
            name="get_incident",
            description="Get detailed information about a specific incident by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "incident_id": {
                        "type": "integer",
                        "description": "The incident ID"
                    }
                },
                "required": ["incident_id"]
            }
        ),
        Tool(
            name="list_evidence",
            description="List evidence files for incidents",
            inputSchema={
                "type": "object",
                "properties": {
                    "incident_id": {
                        "type": "integer",
                        "description": "Filter by incident ID"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of evidence files to return",
                        "default": 100
                    }
                }
            }
        ),
        Tool(
            name="get_risk_assessment",
            description="Get risk assessment for an incident. "
                       "READ-ONLY: This tool cannot execute remediation.",
            inputSchema={
                "type": "object",
                "properties": {
                    "incident_id": {
                        "type": "integer",
                        "description": "The incident ID to assess"
                    }
                },
                "required": ["incident_id"]
            }
        ),
        Tool(
            name="list_approvals",
            description="List approval requests with optional status filter",
            inputSchema={
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["pending", "approved", "rejected", "timeout"],
                        "description": "Filter by approval status"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of approvals to return",
                        "default": 100
                    }
                }
            }
        ),
        Tool(
            name="get_audit_trail",
            description="Get audit trail for incident tracking and compliance",
            inputSchema={
                "type": "object",
                "properties": {
                    "incident_id": {
                        "type": "integer",
                        "description": "Filter by incident ID"
                    },
                    "action": {
                        "type": "string",
                        "description": "Filter by action type"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of audit logs to return",
                        "default": 100
                    }
                }
            }
        ),
        Tool(
            name="get_ai_summary",
            description="Get AI-generated summary for an incident",
            inputSchema={
                "type": "object",
                "properties": {
                    "incident_id": {
                        "type": "integer",
                        "description": "The incident ID"
                    }
                },
                "required": ["incident_id"]
            }
        ),
        Tool(
            name="get_ai_recommendation",
            description="Get AI-powered mitigation recommendations for an incident. "
                       "NOTE: These are recommendations only. All remediation requires "
                       "human approval through the HITL workflow.",
            inputSchema={
                "type": "object",
                "properties": {
                    "incident_id": {
                        "type": "integer",
                        "description": "The incident ID"
                    },
                    "context": {
                        "type": "string",
                        "description": "Additional context for recommendations"
                    }
                },
                "required": ["incident_id"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Execute a tool and return results"""
    try:
        if name == "list_incidents":
            params = {
                "skip": arguments.get("skip", 0),
                "limit": arguments.get("limit", 100)
            }
            if "status" in arguments:
                params["status"] = arguments["status"]
            if "severity" in arguments:
                params["severity"] = arguments["severity"]
            if "service" in arguments:
                params["service"] = arguments["service"]
            
            result = await api_request("GET", "/incidents/", params=params)
            return [TextContent(
                type="text",
                text=f"Found {result['total']} incidents:\n\n" +
                     "\n".join([
                         f"- [{i['incident_id']}] {i['title']} "
                         f"({i['severity']}, {i['status']})"
                         for i in result['items']
                     ])
            )]
        
        elif name == "get_incident":
            incident_id = arguments["incident_id"]
            result = await api_request("GET", f"/incidents/{incident_id}")
            return [TextContent(
                type="text",
                text=f"Incident Details:\n\n"
                     f"ID: {result['incident_id']}\n"
                     f"Title: {result['title']}\n"
                     f"Severity: {result['severity']}\n"
                     f"Status: {result['status']}\n"
                     f"Service: {result.get('service', 'N/A')}\n"
                     f"Created: {result['created_at']}\n"
                     f"Description: {result.get('description', 'N/A')}"
            )]
        
        elif name == "list_evidence":
            params = {"limit": arguments.get("limit", 100)}
            if "incident_id" in arguments:
                params["incident_id"] = arguments["incident_id"]
            
            result = await api_request("GET", "/evidence/", params=params)
            return [TextContent(
                type="text",
                text=f"Found {result['total']} evidence files:\n\n" +
                     "\n".join([
                         f"- [{e['evidence_id']}] {e['file_name']} "
                         f"({e['evidence_type']}, {e['file_size']} bytes)"
                         for e in result['items']
                     ])
            )]
        
        elif name == "get_risk_assessment":
            incident_id = arguments["incident_id"]
            result = await api_request("POST", "/risk/calculate", 
                                      json={"incident_id": incident_id})
            return [TextContent(
                type="text",
                text=f"Risk Assessment:\n\n"
                     f"Assessment ID: {result['assessment_id']}\n"
                     f"Incident ID: {result['incident_id']}\n"
                     f"Risk Score: {result['risk_score']}\n"
                     f"Classification: {result['risk_classification']}\n"
                     f"Recommended Action: {result['recommended_action']}\n\n"
                     f"NOTE: This is READ-ONLY. No remediation will be executed."
            )]
        
        elif name == "list_approvals":
            params = {"limit": arguments.get("limit", 100)}
            if "status" in arguments:
                params["status"] = arguments["status"]
            
            result = await api_request("GET", "/approvals/", params=params)
            return [TextContent(
                type="text",
                text=f"Found {result['total']} approval requests:\n\n" +
                     "\n".join([
                         f"- [{a['approval_id']}] Incident {a['incident_id']}: "
                         f"{a['status']} (requested by {a['requested_by']})"
                         for a in result['items']
                     ])
            )]
        
        elif name == "get_audit_trail":
            params = {"limit": arguments.get("limit", 100)}
            if "incident_id" in arguments:
                params["incident_id"] = arguments["incident_id"]
            if "action" in arguments:
                params["action"] = arguments["action"]
            
            result = await api_request("GET", "/audit/", params=params)
            return [TextContent(
                type="text",
                text=f"Found {result['total']} audit logs:\n\n" +
                     "\n".join([
                         f"- [{log['log_id']}] {log['action']} by {log['user']} "
                         f"at {log['timestamp']}"
                         for log in result['items']
                     ])
            )]
        
        elif name == "get_ai_summary":
            incident_id = arguments["incident_id"]
            result = await api_request("POST", "/copilot/summary",
                                      json={"incident_id": incident_id})
            return [TextContent(
                type="text",
                text=f"AI Summary for Incident {incident_id}:\n\n{result['result']}"
            )]
        
        elif name == "get_ai_recommendation":
            incident_id = arguments["incident_id"]
            payload = {"incident_id": incident_id}
            if "context" in arguments:
                payload["context"] = arguments["context"]
            
            result = await api_request("POST", "/copilot/recommendation",
                                      json=payload)
            return [TextContent(
                type="text",
                text=f"AI Recommendations for Incident {incident_id}:\n\n"
                     f"{result['result']}\n\n"
                     f"⚠️ IMPORTANT: These are recommendations only. "
                     f"All remediation actions require human approval "
                     f"through the HITL workflow."
            )]
        
        else:
            return [TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]
    
    except httpx.HTTPError as e:
        return [TextContent(
            type="text",
            text=f"API Error: {str(e)}"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]


async def main():
    """Run the MCP server"""
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
