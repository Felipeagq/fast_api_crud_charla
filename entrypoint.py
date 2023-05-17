from fastapi import FastAPI
import uvicorn

import app.models.models as model
from app.db.config import engine

from app.routes.routes import router as router_crud
from app.routes.user_management import router as router_user


model.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Book Details",
    description="You can perform CRUD operation by using this API",
    version="1.0.0"
)

@app.get("/")
def hello_world_check():
    return {
        "msg":"Hola Mundo"
    }

app.include_router(router=router_crud,tags=["CRUD"],prefix="/books")
app.include_router(router=router_user,prefix="/user")


if __name__ == "__main__":
    uvicorn.run("entrypoint:app",
                host="localhost",
                reload=True)