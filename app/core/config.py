from pathlib import Path
from pydantic_settings import BaseSettings



class Settings(BaseSettings):
    app_name: str = "AI Video Comprehension API"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000

    class Config:
        env_file = ".env"
        extra = "allow"



settings = Settings()




BASE_DIR = Path(__file__).resolve().parents[2]  
SYSTEM_PROMPT_DIR = BASE_DIR / "storage" / "system_prompts"
SYSTEM_PROMPT_DIR.mkdir(parents=True, exist_ok=True)


