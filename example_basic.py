from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

client = OpenAI()

class CalendarEvent(BaseModel):
    event_name: str
    date: str
    participants: list[str]
    
completion_with_json_output = client.chat.completions.create(
    # setting model
    model="gpt-4o-2024-08-06",
    # setting messages
    messages=[
        {"role": "system", "content": "Extract the event information."},
        {"role": "user", "content": "Joko, Anwar, and Rian are going to a workshop event called 'Friday Booster' on 15 November 2024."},
    ],
    # setting response format
    response_format = {"type": "json_object"},
    # setting temperature. Its for the randomness of the output
    temperature=0.0,
    # setting max tokens. Its for the length of the output
    max_tokens=1000,
    # setting max_completion_tokens. Its for max token usage for content generation + reasoning
    max_completion_tokens=1000,
)

completion_with_structured_format = client.beta.chat.completions.parse(
    model="gpt-4o-2024-08-06",
    messages=[
        {"role": "system", "content": "Extract the event information."},
        {"role": "user", "content": "Joko, Anwar, and Rian are going to a workshop event called 'Friday Booster' on 15 November 2024."},
    ],
    response_format = CalendarEvent
)

print(completion_with_structured_format.choices[0].message.parsed)
print(completion_with_json_output.choices[0].message.content)