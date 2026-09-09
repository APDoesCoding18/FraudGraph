from neo4j import AsyncDriver
from uuid import UUID

class GraphQueries:
    def __init__(self, driver: AsyncDriver):
        self.driver = driver

    async def detect_circular_transactions(self, start_account: UUID, end_account: UUID, min_length: int = 2) -> bool:
        """
        Detects if there is a path from end_account back to start_account of at least min_length hops.
        Used by CIRCULAR_TRANSACTION rule.
        """
        query = """
        MATCH path = (start:Account {id: $end_account})-[:SENT|RECEIVED_BY*2..6]->(end:Account {id: $start_account})
        RETURN count(path) > 0 AS has_cycle
        """
        async with self.driver.session() as session:
            result = await session.run(query, end_account=str(end_account), start_account=str(start_account))
            record = await result.single()
            return record["has_cycle"] if record else False

    async def detect_suspicious_cluster(self, account_id: UUID, min_accounts: int = 5, min_high_risk_transactions: int = 3) -> bool:
        """
        Detects if the account belongs to a cluster meeting the criteria.
        Used by SUSPICIOUS_TRANSACTION_CLUSTER rule.
        """
        query = """
        MATCH (a:Account {id: $account_id})-[:SENT|RECEIVED_BY*1..2]-(cluster_node)
        WITH collect(distinct cluster_node) + a AS cluster
        WHERE size(cluster) >= $min_accounts
        
        UNWIND cluster AS n1
        MATCH (n1)-[:SENT]->(t:Transaction)-[:RECEIVED_BY]->(n2)
        WHERE n2 IN cluster AND t.risk_score >= 25
        
        WITH count(distinct t) AS high_risk_tx_count
        RETURN high_risk_tx_count >= $min_tx AS is_suspicious
        """
        async with self.driver.session() as session:
            result = await session.run(
                query, 
                account_id=str(account_id), 
                min_accounts=min_accounts, 
                min_tx=min_high_risk_transactions
            )
            record = await result.single()
            return record["is_suspicious"] if record else False

    async def detect_fan_in_fan_out(self, account_id: UUID, window_hours: int = 1, threshold: int = 5) -> bool:
        """
        Detects if an account interacts with >= threshold distinct counterparties.
        """
        query = """
        MATCH (a:Account {id: $account_id})-[:SENT|RECEIVED_BY]-(t:Transaction)-[:SENT|RECEIVED_BY]-(counterparty:Account)
        WHERE a <> counterparty
        WITH count(distinct counterparty) AS counterparty_count
        RETURN counterparty_count >= $threshold AS is_fan
        """
        async with self.driver.session() as session:
            result = await session.run(query, account_id=str(account_id), threshold=threshold)
            record = await result.single()
            return record["is_fan"] if record else False

    async def detect_mule_pattern(self, account_id: UUID, min_incoming: int = 5, min_outgoing: int = 3) -> bool:
        """
        Detects if an account receives from >= min_incoming and sends to >= min_outgoing distinct accounts.
        """
        query = """
        MATCH (a:Account {id: $account_id})
        
        OPTIONAL MATCH (sender:Account)-[:SENT]->(:Transaction)-[:RECEIVED_BY]->(a)
        WITH a, count(distinct sender) AS incoming_count
        
        OPTIONAL MATCH (a)-[:SENT]->(:Transaction)-[:RECEIVED_BY]->(receiver:Account)
        WITH incoming_count, count(distinct receiver) AS outgoing_count
        
        RETURN incoming_count >= $min_in AND outgoing_count >= $min_out AS is_mule
        """
        async with self.driver.session() as session:
            result = await session.run(
                query, 
                account_id=str(account_id), 
                min_in=min_incoming, 
                min_out=min_outgoing
            )
            record = await result.single()
            return record["is_mule"] if record else False

from app.graph.client import neo4j_client
graph_queries = GraphQueries(neo4j_client.driver)
