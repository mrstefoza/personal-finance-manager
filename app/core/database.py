import asyncpg
from typing import Optional
from app.core.config import settings


class Database:
    """Database connection manager"""
    
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
    
    async def connect(self):
        """Create database connection pool"""
        if not self.pool:
            self.pool = await asyncpg.create_pool(
                settings.DATABASE_URL,
                min_size=5,
                max_size=20,
                command_timeout=60
            )
            print("✅ Database connection pool created")
    
    async def disconnect(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
            print("🛑 Database connection pool closed")
    
    async def get_pool(self) -> asyncpg.Pool:
        """Get database connection pool"""
        if not self.pool:
            await self.connect()
        return self.pool
    
    async def execute(self, query: str, *args):
        """Execute a query"""
        pool = await self.get_pool()
        return await pool.execute(query, *args)
    
    async def fetch(self, query: str, *args):
        """Fetch multiple rows"""
        pool = await self.get_pool()
        return await pool.fetch(query, *args)
    
    async def fetchrow(self, query: str, *args):
        """Fetch a single row"""
        pool = await self.get_pool()
        return await pool.fetchrow(query, *args)
    
    async def fetchval(self, query: str, *args):
        """Fetch a single value"""
        pool = await self.get_pool()
        return await pool.fetchval(query, *args)


# Create database instance
database = Database()


async def get_db() -> Database:
    """Dependency to get database instance"""
    return database 