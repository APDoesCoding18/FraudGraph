import logging
from app.events.schemas import TransactionEvent
from app.events.idempotency import is_event_processed, mark_event_processing
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update
from app.models.transaction import Transaction
from app.common.enums import TransactionStatus
from app.redis.operations import redis_ops
from app.graph.projection import neo4j_projection
from app.graph.queries import graph_queries
from app.fraud.engine import fraud_engine
from app.repositories.alert import create_alert
from app.schemas.alert import AlertCreate

logger = logging.getLogger(__name__)

async def handle_transaction_event(event: TransactionEvent, session: AsyncSession):
    """
    Core E2E background handler for transaction events.
    """
    logger.info(f"Handling transaction event: {event.transaction_id}")
    
    if await is_event_processed(session, event.transaction_id):
        logger.info(f"Transaction {event.transaction_id} already processed. Skipping.")
        return

    await mark_event_processing(session, event.transaction_id)
    
    try:
        # 1. Record in Redis for rolling window state
        await redis_ops.record_transaction(event)
        
        # 2. Execute Fraud Engine
        # Pass dependencies (DB, Redis, Neo4j) to the engine
        results, score, level = await fraud_engine.evaluate_transaction(
            event,
            db_session=session,
            redis_client=redis_ops,
            graph_queries=graph_queries
        )
        
        # 3. Generate Alert if score >= 25
        if score >= 25:
            triggered_rules = [r.rule_code for r in results if r.triggered]
            alert_data = AlertCreate(
                transaction_id=event.transaction_id,
                risk_score=score,
                risk_level=level,
                triggered_rules=triggered_rules
            )
            await create_alert(session, alert_data)
            logger.info(f"Alert generated for transaction {event.transaction_id} (Score: {score})")

        # 4. Update Transaction status in PostgreSQL
        stmt = update(Transaction).where(Transaction.id == event.transaction_id).values(
            status=TransactionStatus.PROCESSED.value,
            risk_score=score,
            risk_level=level.value
        )
        await session.execute(stmt)
        await session.commit()
        
        # 5. Project to Neo4j asynchronously (happens after PG commit)
        # We also merge accounts just to be safe, though merge_transaction does it
        await neo4j_projection.merge_account(event.sender_account_id)
        await neo4j_projection.merge_account(event.receiver_account_id)
        await neo4j_projection.merge_transaction(event, score, level.value)
        
        logger.info(f"Successfully processed E2E pipeline for transaction {event.transaction_id}")
        
    except Exception as e:
        logger.error(f"Error processing transaction {event.transaction_id}: {e}")
        stmt = update(Transaction).where(Transaction.id == event.transaction_id).values(status=TransactionStatus.FAILED.value)
        await session.execute(stmt)
        await session.commit()
        raise e
