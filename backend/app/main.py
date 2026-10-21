from fastapi import FastAPI
from sqlalchemy import text

from app import models #noqa: F401
from app.core.database import engine
from app.modules.auth.router import router as auth_router
from app.modules.users.router import router as users_router
from app.modules.accounts.router import router as accounts_router


app = FastAPI(
    title="MetaCerta",
    description="Planejamento de metas financeiras com cotações de moedas.",
    version="0.1.0",
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(accounts_router)


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return {"status": "ok", "database": "ok"}
