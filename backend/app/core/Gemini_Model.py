from dotenv import load_dotenv
import os
import json
from langchain.agents import create_agent

load_dotenv()


class Model:
    def __init__(self, model):
        self.API_KEY = os.getenv("GEMINI_API_KEY")
        self.model = model

    @staticmethod
    def writeCode(lines: list[str], fileName: str):
        """
        Writes code to wrote/<fileName>.py
        """
        os.makedirs("wrote", exist_ok=True)

        file_path = os.path.join("wrote", fileName + ".py")

        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        return f"Successfully wrote {file_path}"

    @staticmethod
    def makeDir(name: str):
        """
        Creates a directory.
        """
        try:
            os.makedirs(name, exist_ok=True)
            return {
                "Status": True,
                "Message": f"Directory '{name}' created."
            }
        except Exception as e:
            return {
                "Status": False,
                "Message": str(e)
            }

    @staticmethod
    def makeFile(name: str, path: str):
        """
        Creates an empty python file.
        """
        try:
            os.makedirs(path, exist_ok=True)

            file_path = os.path.join(path, name + ".py")

            with open(file_path, "w", encoding="utf-8"):
                pass

            return {
                "Status": True,
                "Message": f"Created {file_path}"
            }

        except Exception as e:
            return {
                "Status": False,
                "Message": str(e)
            }

    @staticmethod
    def writeFile(path: str, lines: list[str]):
        """
        Writes lines into an existing file.
        """
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)

            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))

            return {
                "Status": True,
                "Message": f"Wrote to {path}"
            }

        except Exception as e:
            return {
                "Status": False,
                "Message": str(e)
            }

    @staticmethod
    def readFile(path: str):
        """
        Reads a file.
        """
        try:
            with open(path, "r", encoding="utf-8") as f:
                return {
                    "Status": True,
                    "Content": f.read()
                }

        except Exception as e:
            return {
                "Status": False,
                "Message": str(e)
            }

    @staticmethod
    def appendFile(path: str, lines: list[str]):
        """
        Appends lines to a file.
        """
        try:
            with open(path, "a", encoding="utf-8") as f:
                f.write("\n")
                f.write("\n".join(lines))

            return {
                "Status": True,
                "Message": f"Updated {path}"
            }

        except Exception as e:
            return {
                "Status": False,
                "Message": str(e)
            }

    @staticmethod
    def deleteFile(path: str):
        try:
            os.remove(path)

            return {
                "Status": True,
                "Message": f"Deleted {path}"
            }

        except Exception as e:
            return {
                "Status": False,
                "Message": str(e)
            }

    @staticmethod
    def writeDirectory(template: str):
        """
        template should be a JSON string like:

        {
            "directories": [
                "src",
                "src/utils",
                "tests"
            ],
            "files": [
                {
                    "path": "src",
                    "name": "main",
                    "lines": [
                        "print('Hello')"
                    ]
                }
            ]
        }
        """
        try:
            data = json.loads(template)

            for directory in data.get("directories", []):
                os.makedirs(directory, exist_ok=True)

            for file in data.get("files", []):
                path = file["path"]
                name = file["name"]
                lines = file.get("lines", [])

                os.makedirs(path, exist_ok=True)

                file_path = os.path.join(path, name + ".py")

                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("\n".join(lines))

            return {
                "Status": True,
                "Message": "Project created successfully."
            }

        except Exception as e:
            return {
                "Status": False,
                "Message": str(e)
            }

    def getResponse(self, msg):
        agent = create_agent(
            model=self.model,
            tools=[
                Model.makeDir,
                Model.makeFile,
                Model.writeFile,
                Model.readFile,
                Model.appendFile,
                Model.deleteFile,
                Model.writeDirectory,
            ],
            system_prompt=(
                "You are an expert software engineer. "
                "Use the provided tools to create directories, files, "
                "read/update existing files, and generate project structures."
            ),
        )

        result = agent.invoke({
            "messages": [
                {
                    "role": "user",
                    "content": msg
                }
            ]
        })

        return result["messages"][-1].content_blocks