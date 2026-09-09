from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List, Optional
from pydantic import BaseModel

from app.api.deps import get_db
from app.schemas.alert import AlertResponse, AlertUpdate
from app.repositories import alert as alert_repo
from app.common.enums import AlertStatus

router = APIRouter()

class AlertStatusUpdate(BaseModel):
    status: AlertStatus

@router.get("", response_model=List[AlertResponse])
async def list_alerts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[AlertStatus] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    status_val = status.value if status else None
    alerts = await alert_repo.get_alerts(db, skip=skip, limit=limit, status=status_val)
    return alerts

@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    alert = await alert_repo.get_alert(db, alert_id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    return alert

@router.patch("/{alert_id}/status", response_model=AlertResponse)
async def update_alert_status(
    alert_id: UUID,
    status_update: AlertStatusUpdate,
    db: AsyncSession = Depends(get_db)
):
    alert = await alert_repo.get_alert(db, alert_id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
        
    # Example logic: Only allow transition if currently OPEN or INVESTIGATING
    if alert.status in [AlertStatus.RESOLVED.value, AlertStatus.FALSE_POSITIVE.value]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change status of a resolved or false positive alert"
        )
        
    update_data = AlertUpdate(status=status_update.status)
    updated_alert = await alert_repo.update_alert(db, alert_id, update_data)
    await db.commit()
    return updated_alert
