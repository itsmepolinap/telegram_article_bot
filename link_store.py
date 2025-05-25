import aiosqlite
import random
from typing import Optional

class LinkAlreadyExists(Exception):
    """Выбрасывается при попытке добавить уже существующую ссылку от пользователя."""
    pass


class LinkStorage:
    """Асинхронный менеджер взаимодействия с SQLite для хранения ссылок по пользователям."""

    def __init__(self, db_file: str):
        self.db_file = db_file
        self.conn: Optional[aiosqlite.Connection] = None

    async def __aenter__(self):
        self.conn = await aiosqlite.connect(self.db_file)
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS user_links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tg_user_id INTEGER NOT NULL,
                link TEXT NOT NULL,
                UNIQUE(tg_user_id, link)
            )
        ''')
        await self.conn.commit()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.conn.close()

    async def insert_link(self, user_id: int, url: str):
        try:
            await self.conn.execute(
                'INSERT INTO user_links (tg_user_id, link) VALUES (?, ?)',
                (user_id, url)
            )
            await self.conn.commit()
        except aiosqlite.IntegrityError:
            raise LinkAlreadyExists("Данная ссылка уже сохранена этим пользователем.")

    async def pop_random_link(self, user_id: int) -> Optional[str]:
        cursor = await self.conn.execute(
            'SELECT id, link FROM user_links WHERE tg_user_id = ?', (user_id,)
        )
        links = await cursor.fetchall()
        if not links:
            return None
        chosen = random.choice(links)
        await self.conn.execute('DELETE FROM user_links WHERE id = ?', (chosen[0],))
        await self.conn.commit()
        return chosen[1]
