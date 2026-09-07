from typing import TypedDict

class ForgeState(TypedDict):
    user_prompt:str
    refined_prompt:str
    task_plan:dict
    WrokingDirectory:str