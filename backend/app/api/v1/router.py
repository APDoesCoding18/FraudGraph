from fastapi import APIRouter
from app.database.postgres import check_db_health
from app.api.v1 import transactions
from app.api.v1 import alerts
from app.api.v1 import accounts
from app.api.v1 import auth
from app.api.v1 import cases
from app.api.v1 import assistant

api_router = APIRouter()

api_router.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_router.include_router(accounts.router, prefix="/accounts", tags=["accounts"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(cases.router, prefix="/cases", tags=["cases"])
api_router.include_router(assistant.router, prefix="/assistant", tags=["assistant"])

@api_router.get("/health")
async def health_check():
    db_ok = await check_db_health()
    return {"status": "ok", "database": "ok" if db_ok else "unreachable"}
