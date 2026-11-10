import json
import os
from dotenv import load_dotenv
from openai import OpenAI
from tools import TOOLS, run_tool

load_dotenv()


SYSTEM_PROMPT = """
You are a property-management assistant for a small landlord . 

Scope : 
- You answer questions about the rent tenants and units , using only the tools provided to you . 
- If a question is not about the property management, politely say you can't help with that . 

Tool rules : 
- Never guess a number . If you need the rent data , call the tool . 
- If the tool returns the "unknown unit" say the unit was not found . Do not invent the data . 

Answer format : 
- if the data is in the tabular form then return the data in the tabular form otherwise Reply in at most two short sentences . 
- Always include the unit number and the amount with the $ sign ."""

baseurl = os.getenv("LLM_BASE_URL")
api_key = os.getenv("LLM_API_KEY")
model = os.getenv("LLM_MODEL")
client = OpenAI(base_url=baseurl, api_key=api_key)


def run_agent(question: str, max_steps: int = 5) -> str | None:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]
    for step in range(max_steps):
        initial_response = client.chat.completions.create(
            messages=messages, model=model
        )
        llm_respnose = initial_response.choices[0].message
        # we forgot to add this lllm reponse to message earlier
        messages.append(llm_respnose)

        if not llm_respnose.tool_calls:
            # if llm didn't asked for any tool_call mean this is the final answer
            return llm_respnose.content

        for call in llm_respnose.tool_calls:
            args = json.loads(call.function.arguments)
            print(
                f"step {step}: model called tool for {call.function.name} with args {args} "
            )
            tool_response = run_tool(call.function.name, args)
            messages.append(
                {"role": "tool", "content": tool_response, "tool_call_id": call.id}
            )

        return f"Agent ran out of tool calls max limit was {max_steps} and you hit the limit"


print(
    run_agent(
        "how much rent does the unit 605 owe today also give me for the 101 and the 700 ? "
    )
)


# basically i got this datata :
# I am unable to retrieve the rent data for unit 101 and unit 700 because they were not found in the system. For unit 605, I cannot provide the amount without calling the tool; please allow me to check.

# Here is the data for unit 605: Unit 605 owes $1,200 today.
# lets feed some data here
