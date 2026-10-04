from neo4j import AsyncDriver, RoutingControl

from backend.core.pagination import Pagination
from backend.core.settings import Settings


class Neo4jRepository:
    def __init__(self, driver: AsyncDriver) -> None:
        self._driver = driver

    async def add_friend(self, name: str, friend_name: str) -> None:
        await self._driver.execute_query(
            "MERGE (a:Person {name: $name}) "
            "MERGE (friend:Person {name: $friend_name}) "
            "MERGE (a)-[:KNOWS]-(friend)",
            name=name,
            friend_name=friend_name,
            database_=Settings.NEO4J_DB,
        )

    async def remove_friend(self, name: str, friend_name: str) -> None:
        await self._driver.execute_query(
            "MATCH (:Person {name: $name})-[r:KNOWS]-(:Person {name: $friend_name}) DELETE r",
            name=name,
            friend_name=friend_name,
            database_=Settings.NEO4J_DB,
        )

    async def are_friends(self, name: str, friend_name: str) -> bool:
        records, _, _ = await self._driver.execute_query(
            "MATCH (:Person {name: $name})-[:KNOWS]-(:Person {name: $friend_name}) "
            "RETURN true AS found LIMIT 1",
            name=name,
            friend_name=friend_name,
            database_=Settings.NEO4J_DB,
            routing_=RoutingControl.READ,
        )
        return bool(records)

    async def get_friends(self, name: str, pagination: Pagination) -> list[str]:
        records, _, _ = await self._driver.execute_query(
            "MATCH (a:Person {name: $name})-[:KNOWS]-(friend:Person) "
            "RETURN DISTINCT friend.name AS friend_name ORDER BY friend_name "
            "SKIP $offset LIMIT $limit",
            name=name,
            offset=pagination.offset,
            limit=pagination.limit,
            database_=Settings.NEO4J_DB,
            routing_=RoutingControl.READ,
        )
        return [record["friend_name"] for record in records]
