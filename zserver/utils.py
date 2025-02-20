import os

from dotenv import load_dotenv

load_dotenv()
def get_env_var() -> dict[str, str]:
    env_var = {}
    env_var["GOOGLE_CLIENT_ID"] = os.getenv("GOOGLE_CLIENT_ID")
    env_var["GOOGLE_REDIRECT_URI"] = os.getenv("GOOGLE_REDIRECT_URI")
    return env_var
