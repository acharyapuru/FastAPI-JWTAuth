from fastapi import FastAPI, Depends
from src.routers import authentication
from src.database import Base, engine
from src.models import User
from src.utils.auth import get_current_user

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(authentication.route)

@app.get("/index")
def index(current_user:User = Depends(get_current_user)):
    return "Hello World"


# if __name__ == "__main__":
#     uvicorn.run(
#         "main:app",
#         host="0.0.0.0",
#         port=8000,
#         log_level="info",
#         reload=True
#     )