from neo4j import AsyncGraphDatabase
from app.core.config import settings

class Neo4jClient:
    def __init__(self):
        self.driver = AsyncGraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD)
        )

    async def close(self):
        await self.driver.close()

neo4j_client = Neo4jClient()

async def get_neo4j():
    return neo4j_client.driver
