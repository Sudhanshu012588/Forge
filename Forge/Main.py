import subprocess
from Agent.Agent_main import main
from dotenv import load_dotenv
import os
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
WorkSpace = os.getenv("WORKSPACE")
main(api_key,WorkSpace)