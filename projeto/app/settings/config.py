from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
	model_config= SettingsConfigDict(env_file="app/settings/.env")
	
	db_user: str
	db_pass: str
	
	db_host: str
	db_port: int
	db_name: str
