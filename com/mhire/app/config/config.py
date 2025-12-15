import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            
            # Other configs...
            cls._instance.openai_api_key = os.getenv("OPENAI_API_KEY")
            cls._instance.openai_model = os.getenv("OPENAI_MODEL")

            #document ai configs
            cls._instance.google_application_credential = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            cls._instance.project_id = os.getenv("PROJECT_ID")
            cls._instance.location = os.getenv("LOCATION")
            cls._instance.processor_id = os.getenv("PROCESSOR_ID")
            cls._instance.processor_version = os.getenv("PROCESSOR_VERSION")
        return cls._instance