import subprocess

def ls():
    return subprocess.call(["ls"])

def mkdir(Dir):
    return subprocess.call(["mkdir",Dir])

def delete(path):
    return subprocess.call(["rm -rf",path])

def run(path):
    return subprocess.call(["python3",path])    