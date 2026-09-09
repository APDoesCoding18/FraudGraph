from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from typing import List, Optional
from app.models.alert import Alert
from app.schemas.alert import AlertCreate, AlertUpdate

async def create_alert(db: AsyncSession, alert_data: AlertCreate) -> Optional[Alert]:
    # Alert is only generated if risk_score >= 25
    if alert_data.risk_score < 25:
        return None
        
    db_alert = Alert(
        transaction_id=alert_data.transaction_id,
        risk_score=alert_data.risk_score,
        risk_level=alert_data.risk_level.value,
        triggered_rules=alert_data.triggered_rules,
    )
    db.add(db_alert)
    await db.flush()
    return db_alert

async def get_alert(db: AsyncSession, alert_id: UUID) -> Optional[Alert]:
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    return result.scalar_one_or_none()

async def get_alerts(db: AsyncSession, skip: int = 0, limit: int = 100, status: Optional[str] = None) -> List[Alert]:
    stmt = select(Alert).order_by(Alert.created_at.desc())
    if status:
        stmt = stmt.where(Alert.status == status)
    stmt = stmt.offset(skip).limit(limit)
    
    result = await db.execute(stmt)
    return list(result.scalars().all())

async def update_alert(db: AsyncSession, alert_id: UUID, update_data: AlertUpdate) -> Optional[Alert]:
    alert = await get_alert(db, alert_id)
    if not alert:
        return None
        
    if update_data.status:
        alert.status = update_data.status.value
        
    await db.flush()
    return alert
