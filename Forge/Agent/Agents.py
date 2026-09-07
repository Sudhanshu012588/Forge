from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, MessagesState, START, END
from langchain_core.tools import tool
from Prompts.Prompts import PromptEnhancer,TaskScheduler
from Agent.Context import ForgeState
from FilesCommand.FileCommand import explore, write_file
from TerminalCommands.Commands import ls,mkdir,delete,run,touch,cd
import json

def get_text(response):
    content = response.content

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        return "".join(
            item.get("text", "")
            for item in content
            if item.get("type") == "text"
        )

    return str(content)

def task_scheduler(llm, state: ForgeState):
    task_scheduler_prompt = TaskScheduler()
    response = llm.invoke([
        {
            "role": "system",
            "content": task_scheduler_prompt
        },
        {
            "role": "user",
            "content": state["refined_prompt"]
        }
    ])

    content = get_text(response)
    return {"task_plan": json.loads(content)}

def prompt_refiner(llm,state:ForgeState,WorkingDirectory):
    prompt_enhancer_prompt = PromptEnhancer()
    response = llm.invoke([
        {
            "role": "system",
            "content": prompt_enhancer_prompt
        },
        {
            "role": "user",
            "content": state["user_prompt"]
        }
    ])
    return{"refined_prompt": get_text(response)}


@tool 
def readCodeBase(path):
    files = explore.invoke({"dir":path})

    file_list = "\n".join(f"- {file}" for file in files)

    prompt = f"""
    Here is the file structure of the current codebase:

    {file_list}

    Use this file structure when deciding which files you need to inspect.
    Do not assume that files exist if they are not listed above.
    """
    return prompt


def task_executor(llm, task):

    tools = [explore,write_file,ls,mkdir,delete,run,touch,cd,readCodeBase]
    tool_map = {
        tool.name: tool
        for tool in tools
    }
    llm_with_tools = llm.bind_tools(tools)
    messages = [
                {
                    "role": "system",
                    "content": """
        You are Forge's Task Executor.

        Execute the provided task using the available tools.

        You MUST actually perform the task.
        Do not merely explain what should be done.

        Use the tools whenever necessary.

        When the task has been successfully completed,
        respond that the task is completed.

        If the task cannot be completed,
        respond that the task failed.

        ## Write the code in the {WorkingDirectory} you can modify the path inside the {WorkingDirectory} to write inside a specific file 
        """
                },
                {
                    "role": "user",
                    "content": f"""
        Task ID: {task["id"]}

        Task:
        {task["description"]}

        Current status:
        {task["status"]}"""}]
    while True:
        response = llm_with_tools.invoke(messages)
        messages.append(response)
        if not response.tool_calls:break
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            print(f"🔧 Calling {tool_name}")
            print(f"   Arguments: {tool_args}")
            tool_result = tool_map[tool_name].invoke(tool_args)
            messages.append({"role": "tool","content": str(tool_result),"tool_call_id": tool_call["id"]})
    return response