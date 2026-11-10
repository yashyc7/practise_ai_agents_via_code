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
    }
]


# 3. Name -> real function
REGISTRY = {"get_rent_due": get_rent_due}

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
        "how much rent does the unit 605 owe today also give me for the 101 and the 700 ? "
    )
)
