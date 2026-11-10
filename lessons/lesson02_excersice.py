# Lesson Agent, tool and harness in one file
from email import message
import json
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(base_url=os.getenv("LLM_BASE_URL"), api_key=os.getenv("LLM_API_KEY"))
model = os.getenv("LLM_MODEL")

# lets create the tool for fake data


def get_rent_due(unit: str) -> str:
    fake_ledger = {"605": 1450.00, "101": 1250.00}
    # parsing this dict into json format
    return json.dumps({"unit": unit, "rent_due": fake_ledger.get(unit, 0.00)})


def get_tenant_name(unit: str) -> str:
    fake_tenant = {"605": "John Doe", "101": "Jane Doe"}
    return json.dumps({"unit": unit, "tenant_name": fake_tenant.get(unit, "Unknown")})


def get_payment_history(unit: str, months: int) -> str:
    # get the payment history for the given unit and months if the months are large then make the list large according to the months value
    payment_history = []
    for i in range(int(months)):
        payment_history.append(1000.00 + i)
    return json.dumps({"unit": unit, "payment_history": payment_history})
    fake_payment_history = {
        "605": [1000.00, 1100.00, 1200.00],
        "101": [900.00, 1000.00, 1100.00],
    }
    return json.dumps({"unit": unit, "payment_history": payment_history})

    # the menu model sees


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
    {
        "type": "function",
        "function": {
            "name": "get_payment_history",
            "description": "Get the payment history for the given unit",
            "parameters": {
                "type": "object",
                "properties": {
                    "unit": {
                        "type": "string",
                        "description": "The unit number, e.g. 605 ",
                    },
                    "months": {
                        "type": "string",
                        "description": "the months for which we have to return the payment history consider three as 3 and  if said 2 years then consider 24 months",
                    },
                },
                "required": ["unit", "months"],
            },
        },
    },
]


# 3. Name -> real function
REGISTRY = {
    "get_rent_due": get_rent_due,
    "get_tenant_name": get_tenant_name,
    "get_payment_history": get_payment_history,
}

# 4. The loop


def run_agent(question: str, max_steps: int = 5) -> str | None:

    messages = [{"role": "user", "content": question}]
    # looping the question in the max_steps loop
    for step in range(max_steps):
        response = client.chat.completions.create(
            model=model, messages=messages, tools=TOOLS
        )

        llm_response = response.choices[0].message
        messages.append(llm_response)

        if not llm_response.tool_calls:
            # llm didn't asked for any tool_call
            return llm_response.content

        # if it requested 'n' tool calls
        for call in llm_response.tool_calls:
            args = json.loads(call.function.arguments)
            print(
                f"step {step}: model called tool for {call.function.name} with args {args} "
            )

            # actual tool calling

            result = REGISTRY[call.function.name](**args)

            # append the tool result to the message

            messages.append(
                {"role": "tool", "tool_call_id": call.id, "content": result}
            )

    return "Stopped, tool call limit reached ! "


print(
    run_agent(
        "how much rent does the unit 605 owe today also give me for the 101 and the 700 ? also give me the tenant name for the unit 605 and the payment history for the unit 605 for the last 12 months and then give me the payment history for the unit 101 for last 1 year"
    )
)
