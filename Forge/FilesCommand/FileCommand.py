import os
from langchain_core.tools import tool


@tool
def explore(dir: str):
    """Return a list containing all files in the given directory."""
    result = []

    for root, dirs, files in os.walk(dir):
        for file in files:
            path = os.path.join(root, file)
            result.append(path)

    return result

@tool
def write_file(path, content):
    """given the path:string, and context:string as parameters this Function allows to write in a txt file """
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    return f"Successfully wrote {path}"