import os

## This function will return an array which includes all the flies and folder in the dir.
def explore(dir):
    result = []
    for root, dirs, files in os.walk(dir):
            for file in files:
                path = os.path.join(root, file)
                result.append(path)
    return result

def write_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"Successfully wrote {path}"