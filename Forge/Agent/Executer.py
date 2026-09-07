from Agent.Context import ForgeState
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from FilesCommand.FileCommand import explore,write_file
from TerminalCommands.Commands import ls,mkdir,delete,cd,touch,run
from Prompts.Prompts import task_scheduling

import os


load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
def get_text(response):
    content = response.content

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        return "".join(
            item.get("text", "")
            for item in content
            if isinstance(item, dict) and item.get("type") == "text"
        )

    return str(content)



if not api_key:
    raise ValueError(
        "GEMINI_API_KEY was not found. Make sure it is defined in .env"
    )


llm = ChatGoogleGenerativeAI(
    model="gemini-3.7-flash",
    temperature=0,
    google_api_key=api_key
)

llm_with_tools=llm.bind_tools([explore,write_file,ls,mkdir,delete,cd,touch,run])
class Executor:

    def __init__(self):
        self.prompt = task_scheduling()

    def agent(self, state: ForgeState):

        response = llm_with_tools.invoke([
            {
                "role": "system",
                "content": self.prompt
            },
            {
                "role": "user",
                "content": state["refined_prompt"]
            }
        ])

        return {
            "task_plan": get_text(response)
        }