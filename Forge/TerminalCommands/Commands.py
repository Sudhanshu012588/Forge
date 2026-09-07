import subprocess
from langchain_core.tools import tool

@tool
def ls():
    """This function returns the folder structure of the curent directory"""
    return subprocess.call(["ls"])

@tool
def mkdir(Dir):
    """Given the input parameter Dir i.e a string it will create a folder/Directory named Dir in the current location"""
    return subprocess.call(["mkdir",Dir])

@tool
def delete(path):
    """Given the path: String as the input parameter this function will delete the the folder at the path"""
    return subprocess.call(["rm -rf",path])

@tool
def run(path):
    """Given the path:string as input path-> a python script This function will run the python script"""
    return subprocess.call(["python3",path])    

@tool
def touch(name):
    """Write into a File"""
    return subprocess.call(["touch",name])

@tool
def cd(path):
    """Go to a specific directory"""
    return subprocess.call(["cd ./",path])