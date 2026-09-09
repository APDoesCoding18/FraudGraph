from neo4j import AsyncDriver
from uuid import UUID
from datetime import datetime
from app.events.schemas import TransactionEvent

class GraphProjection:
    def __init__(self, driver: AsyncDriver):
        self.driver = driver

    async def merge_account(self, account_id: UUID, created_at: datetime = None) -> None:
        """
        Merge an account node into the graph. 
        Usually created_at is only set when the account is first created.
        """
        if not created_at:
            created_at = datetime.utcnow()
            
        query = """
        MERGE (a:Account {id: $account_id})
        ON CREATE SET a.created_at = $created_at
        """
        async with self.driver.session() as session:
            await session.run(query, account_id=str(account_id), created_at=created_at.isoformat())

    async def merge_transaction(self, event: TransactionEvent, risk_score: int, risk_level: str) -> None:
        """
        Merge transaction node and create SENT and RECEIVED_BY relationships.
        Expects accounts to exist, but MERGE will create them if missing.
        """
        query = """
        MERGE (sender:Account {id: $sender_id})
        MERGE (receiver:Account {id: $receiver_id})
        MERGE (t:Transaction {id: $tx_id})
        ON CREATE SET 
            t.amount = $amount,
            t.timestamp = $timestamp,
            t.risk_score = $risk_score,
            t.risk_level = $risk_level
        ON MATCH SET
            t.risk_score = $risk_score,
            t.risk_level = $risk_level
        MERGE (sender)-[:SENT]->(t)
        MERGE (t)-[:RECEIVED_BY]->(receiver)
        """
        async with self.driver.session() as session:
            await session.run(
                query,
                sender_id=str(event.sender_account_id),
                receiver_id=str(event.receiver_account_id),
                tx_id=str(event.transaction_id),
                amount=event.amount,
                timestamp=event.timestamp.isoformat(),
                risk_score=risk_score,
                risk_level=risk_level
            )

neo4j_projection = GraphProjection(neo4j_client.driver)
