import json


def get_rent_due(unit: str) -> str:
    ledger = {"605": 1000.00, "101": 1100.00, "700": 1200.00}
    return json.dumps({"unit": unit, "rent_due": ledger.get(unit, 0.00)})


def get_tenant_name(unit: str) -> str:
    tenant_names = {"605": "John Doe", "101": "Jane Doe", "700": "Jim Doe"}
    return json.dumps({"unit": unit, "tenant_name": tenant_names.get(unit, "Unknown")})


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_rent_due",
            "description": "Get the rent due for a given unit",
            "parameters": {
                "type": "object",
                "properties": {
                    "unit": {
                        "type": "string",
                        "description": "The unit number, e.g. 605",
                    }
                },
                "required": ["unit"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_tenant_name",
            "description": "Get the tenant name for the given unit",
            "parameters": {
                "type": "object",
                "properties": {
                    "unit": {
                        "type": "string",
                        "description": "The unit number, e.g. 605",
                    }
                },
                "required": ["unit"],
            },
        },
    },
]

REGISTRY = {
    "get_rent_due": get_rent_due,
    "get_tenant_name": get_tenant_name,
}


def run_tool(name: str, args: dict) -> str:

    fn = REGISTRY.get(name)

    if not fn:
        return json.dumps({"error": f"Function not found {name}"})
    try:
        return json.dumps(fn(**args))
    except Exception as e:
        return json.dumps({"error": f"Error calling function {name}: {e}"})
