import sys
import json
from typing import Dict, Any

try:
    from backend.src.skills import (
        calculate_tuition_quote,
        schedule_placement_test,
        create_escalation_ticket,
    )
    from backend.src.metrics import metrics_collector
except ImportError:
    from src.skills import (
        calculate_tuition_quote,
        schedule_placement_test,
        create_escalation_ticket,
    )
    from src.metrics import metrics_collector


# MCP Tool Definitions Schema
MCP_TOOLS_MANIFEST = [
    {
        "name": "calculate_tuition_quote",
        "description": "Calculate official language tuition in Colombian Pesos (COP) with applicable discounts (Early Bird, Cajas de Compensacion, Student) and installment plans.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "program_type": {
                    "type": "string",
                    "enum": ["standard", "intensive", "business", "exam_prep"],
                    "description": "Program type track.",
                },
                "payment_plan": {
                    "type": "string",
                    "enum": ["upfront", "installments"],
                    "description": "Payment modality.",
                },
                "discount_code": {
                    "type": "string",
                    "enum": ["none", "early_bird", "family", "compensar_a", "compensar_b", "colsubsidio_a", "comfama_a", "university_student"],
                    "description": "Applicable discount code or corporate agreement.",
                },
            },
            "required": ["program_type"],
        },
    },
    {
        "name": "schedule_placement_test",
        "description": "Schedule a free diagnostic language level test for prospective students.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "student_name": {"type": "string", "description": "Full name of the student"},
                "language": {"type": "string", "description": "Language to be tested (English, French, German, Italian, Portuguese)"},
                "modality": {"type": "string", "enum": ["online", "campus_bogota", "campus_medellin"], "description": "Testing modality"},
                "email": {"type": "string", "description": "Student contact email"},
            },
            "required": ["student_name", "language"],
        },
    },
    {
        "name": "get_academy_metrics",
        "description": "Retrieve real-time operational metrics: total queries, cache hits, token usage, and human escalation rates.",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
]


def handle_mcp_call(method: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Execute MCP JSON-RPC protocol requests."""
    if method == "tools/list":
        return {"tools": MCP_TOOLS_MANIFEST}
    elif method == "tools/call":
        name = params.get("name")
        arguments = params.get("arguments", {})

        if name == "calculate_tuition_quote":
            result = calculate_tuition_quote(
                program_type=arguments.get("program_type", "standard"),
                payment_plan=arguments.get("payment_plan", "upfront"),
                discount_code=arguments.get("discount_code", "none"),
            )
            return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}

        elif name == "schedule_placement_test":
            result = schedule_placement_test(
                student_name=arguments.get("student_name", "Prospective Student"),
                language=arguments.get("language", "English"),
                modality=arguments.get("modality", "online"),
                email=arguments.get("email"),
            )
            return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}

        elif name == "get_academy_metrics":
            result = metrics_collector.get_metrics()
            return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}

        else:
            return {"isError": True, "content": [{"type": "text", "text": f"Unknown tool: {name}"}]}

    return {"isError": True, "content": [{"type": "text", "text": f"Unsupported method: {method}"}]}


def run_mcp_stdio_server():
    """Run standard stdio loop for Model Context Protocol (MCP) clients."""
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            request = json.loads(line)
            req_id = request.get("id")
            method = request.get("method", "")
            params = request.get("params", {})

            result = handle_mcp_call(method, params)
            response = {"jsonrpc": "2.0", "id": req_id, "result": result}
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()
        except Exception as e:
            sys.stderr.write(f"MCP Server error: {e}\n")


if __name__ == "__main__":
    run_mcp_stdio_server()
