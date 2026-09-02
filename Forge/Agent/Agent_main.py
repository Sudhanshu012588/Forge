from Prompts.Prompts import MiddleMen,PromptEnhancer,TaskScheduler
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, MessagesState, START, END
from FilesCommand.FileCommand import explore
from typing import TypedDict


class ForgeState(TypedDict):
    user_prompt: str
    refined_prompt: str
    task_plan: str
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

def readCodeBase(path):
    files = explore(path)

    file_list = "\n".join(f"- {file}" for file in files)

    prompt = f"""
    Here is the file structure of the current codebase:

    {file_list}

    Use this file structure when deciding which files you need to inspect.
    Do not assume that files exist if they are not listed above.
    """
    return prompt



def main(api_key,path):

    MiddleMenPrompt = MiddleMen()
    CodeBase_context = readCodeBase(path)
    llm = ChatGoogleGenerativeAI(
        model="gemini-3.7-flash",
        temperature=0,
        google_api_key=api_key
    )


    ## Prompt Refiner
    prompt_enhancer_prompt = PromptEnhancer()

    def prompt_refiner(state:ForgeState):

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

        return {
            "refined_prompt": get_text(response)
        }

    task_scheduler_prompt = TaskScheduler()

    def task_scheduler(state:ForgeState):

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

        return {
            "task_plan": get_text(response)
        }

    graph_builder = StateGraph(MessagesState)

    graph_builder.add_node("promptRefiner",prompt_refiner)
    graph_builder.add_node("Task_Scheduler",TaskScheduler)
    graph_builder = StateGraph(ForgeState)

    graph_builder.add_node("promptRefiner", prompt_refiner)
    graph_builder.add_node("taskScheduler", task_scheduler)

    graph_builder.add_edge(START, "promptRefiner")
    graph_builder.add_edge("promptRefiner", "taskScheduler")
    graph_builder.add_edge("taskScheduler", END)

    graph = graph_builder.compile()

    starting_prompt = input(
        "What would you like Forge to do? ❯ "
    )

    if starting_prompt.lower() == "exit":
        return

    state = graph.invoke({
        "user_prompt": starting_prompt,
        "refined_prompt": "",
        "task_plan": ""
    })

    print("\nRefined Prompt:")
    print(state["refined_prompt"])

    print("\nTask Plan:")
    print(state["task_plan"])


    while True:

        user_input = input("\n❯ ")

        if user_input.lower() == "exit":
            break

        state = graph.invoke({
            "user_prompt": user_input,
            "refined_prompt": "",
            "task_plan": ""
        })

        print("\nRefined Prompt:")
        print(state["refined_prompt"])

        print("\nTask Plan:")
        print(state["task_plan"])