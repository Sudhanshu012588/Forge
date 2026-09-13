from Prompts.Prompts import MiddleMen,PromptEnhancer,TaskScheduler
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, MessagesState, START, END
from FilesCommand.FileCommand import explore
from typing import TypedDict
from Agent.Context import ForgeState
from Agent.Agents import task_scheduler,prompt_refiner,task_executor
from langchain_ollama import ChatOllama



def main(api_key,path):

    MiddleMenPrompt = MiddleMen()
    # llm = ChatGoogleGenerativeAI(
    #     model="gemini-3.7-flash",
    #     temperature=0,
    #     google_api_key=api_key
    # )
    llm = ChatOllama(
        model="qwen3:8b",
        temperature=0
    )
    ## Prompt Refiner
    graph_builder = StateGraph(ForgeState)
    graph_builder.add_node("promptRefiner",lambda state:prompt_refiner(llm,state))
    graph_builder.add_node("task_scheduler",lambda state:task_scheduler(llm,state))

    graph_builder.add_edge(START, "promptRefiner")
    graph_builder.add_edge("promptRefiner", "task_scheduler")
    graph_builder.add_edge("task_scheduler", END)

    graph = graph_builder.compile()

    # starting_prompt = input(
    #     "What would you like Forge to do? ❯ "
    # )

    # if starting_prompt.lower() == "exit":
    #     return

    state = graph.invoke({
        "user_prompt": MiddleMenPrompt,
        "refined_prompt": "",
        "task_plan": "",
        "WrokingDirectory":path

    })

    # print("\nRefined Prompt:")
    # print(state["refined_prompt"])

    # print("\nTask Plan:")
    # print(state["task_plan"]);

    Start = True
    while True:
        if Start:
            user_input = input("\nWhat would you like Forge to do?\n❯ ")
            Start = False
        else:
            user_input = input("\n❯ ")

        if user_input.lower() == "exit":
            print("Thank You!")
            break
        state = graph.invoke({
            "user_prompt": user_input,
            "refined_prompt": "",
            "task_plan": {},
            "WrokingDirectory": path
        })
        print("\nRefined Prompt:")
        print(state["refined_prompt"])
        print("\nTask Plan:")
        print(state["task_plan"])
        for task in state["task_plan"]["tasks"]:
            print(f"\nExecuting Task {task['id']}")
            print(task["description"])
            result = task_executor(llm, task,state)
            print(result.content)
            task["status"] = "completed"
        
        