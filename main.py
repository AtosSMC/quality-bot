from fastapi import FastAPI
from routers import bot

app = FastAPI()

# Initialize the database
#Base.metadata.create_all(bind=engine)

app.include_router(bot.router)