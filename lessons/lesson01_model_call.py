import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
# reads the three settings from the .env

client = OpenAI(base_url=os.getenv("LLM_BASE_URL"), api_key=os.getenv("LLM_API_KEY"))

# configuring message for sending it to the model

messages = [
    {
        "role": "system",
        "content": "You are an assistant for a small landlord. if you don't know about the property, you should say i don't know about this property you are talking about.",
    },
    {"role": "user", "content": "How much rent does unit 605 owe today?"},
]

response = client.chat.completions.create(
    model=os.getenv("LLM_MODEL"), messages=messages
)


print(response.choices[0].message.content)
