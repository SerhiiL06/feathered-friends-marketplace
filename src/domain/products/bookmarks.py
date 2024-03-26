from src.repositories.tools.redistools import RedisRepository


class BookmarkDomain:
    def __init__(self) -> None:
        self.repo = RedisRepository()

    async def update_bookmark(self, session_key: str, product_slug: str) -> dict:

        return await self.repo.update_bookmark(session_key, product_slug)

    async def bookmarks_list(self, session_key: str) -> list:
        return await self.repo.get_bookmarks(session_key)
