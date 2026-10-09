import sys
from pathlib import Path

here = Path(__file__).resolve().parent
env_file = here / ".env"

print("Python being used :", sys.executable)
print("Script folder     :", here)
print(".env exists here  :", env_file.exists())
print("Files in folder   :", sorted(p.name for p in here.iterdir() if p.name != "venv"))

try:
    from dotenv import dotenv_values
    vals = dotenv_values(env_file)
    print("Names found       :", list(vals.keys()))
    url = vals.get("DATABASE_URL")
    print("DATABASE_URL set  :", bool(url))
    if url:
        print("Starts with       :", url[:13])
        print("Has [ or ] in it  :", "[" in url or "]" in url)
except ImportError:
    print("python-dotenv is NOT installed in this Python")