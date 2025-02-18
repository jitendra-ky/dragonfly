from dotenv import load_dotenv
import os
from typing import Dict

load_dotenv()
def get_env_var() -> Dict[str, str]:
    env_var = {}
    env_var['GOOGLE_CLIENT_ID'] = os.getenv('GOOGLE_CLIENT_ID')
    env_var['GOOGLE_REDIRECT_URI'] = os.getenv('GOOGLE_REDIRECT_URI')
    return env_var