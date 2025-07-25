"""Database management for the cloud native testing platform."""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
import asyncpg
import pymongo
from pymongo import MongoClient
from dataclasses import dataclass
from src.config import DatabaseConfig

logger = logging.getLogger(__name__)


@dataclass
class QueryResult:
    """Database query result container."""
    data: List[Dict[str, Any]]
    count: int
    execution_time: float
    success: bool
    error: Optional[str] = None


class PostgreSQLManager:
    """PostgreSQL database manager."""
    
    def __init__(self, config: DatabaseConfig):
        """Initialize PostgreSQL connection manager."""
        self.config = config
        self.pool = None
        self._connection_string = (
            f"postgresql://{config.user}:{config.password}@"
            f"{config.host}:{config.port}/{config.name}"
        )
    
    async def connect(self) -> None:
        """Establish connection pool to PostgreSQL."""
        try:
            self.pool = await asyncpg.create_pool(
                self._connection_string,
                min_size=5,
                max_size=self.config.pool_size,
                command_timeout=30
            )
            logger.info("PostgreSQL connection pool established")
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Close all connections in the pool."""
        if self.pool:
            await self.pool.close()
            logger.info("PostgreSQL connection pool closed")
    
    async def execute_query(self, query: str, *args) -> QueryResult:
        """Execute a SELECT query."""
        start_time = datetime.now()
        try:
            async with self.pool.acquire() as conn:
                result = await conn.fetch(query, *args)
                data = [dict(row) for row in result]
                execution_time = (datetime.now() - start_time).total_seconds()
                
                return QueryResult(
                    data=data,
                    count=len(data),
                    execution_time=execution_time,
                    success=True
                )
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Query execution failed: {e}")
            return QueryResult(
                data=[],
                count=0,
                execution_time=execution_time,
                success=False,
                error=str(e)
            )
    
    async def execute_command(self, command: str, *args) -> bool:
        """Execute INSERT, UPDATE, DELETE commands."""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute(command, *args)
                return True
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            return False
    
    async def create_user_table(self) -> bool:
        """Create users table for testing."""
        query = """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            uuid VARCHAR(36) UNIQUE NOT NULL,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(150) UNIQUE NOT NULL,
            age INTEGER CHECK (age >= 0 AND age <= 150),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE
        );
        """
        return await self.execute_command(query)
    
    async def create_product_table(self) -> bool:
        """Create products table for testing."""
        query = """
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            uuid VARCHAR(36) UNIQUE NOT NULL,
            name VARCHAR(200) NOT NULL,
            category VARCHAR(100),
            price DECIMAL(10,2) NOT NULL,
            stock INTEGER DEFAULT 0,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_available BOOLEAN DEFAULT TRUE
        );
        """
        return await self.execute_command(query)
    
    async def create_order_table(self) -> bool:
        """Create orders table for testing."""
        query = """
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            uuid VARCHAR(36) UNIQUE NOT NULL,
            user_id INTEGER REFERENCES users(id),
            product_id INTEGER REFERENCES products(id),
            quantity INTEGER NOT NULL CHECK (quantity > 0),
            total_amount DECIMAL(12,2) NOT NULL,
            status VARCHAR(50) DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        return await self.execute_command(query)


class MongoDBManager:
    """MongoDB database manager."""
    
    def __init__(self, host: str = "localhost", port: int = 27017, database: str = "taap_mongo"):
        """Initialize MongoDB connection manager."""
        self.host = host
        self.port = port
        self.database_name = database
        self.client = None
        self.database = None
    
    def connect(self) -> None:
        """Establish connection to MongoDB."""
        try:
            self.client = MongoClient(f"mongodb://{self.host}:{self.port}/")
            self.database = self.client[self.database_name]
            # Test connection
            self.client.admin.command('ping')
            logger.info("MongoDB connection established")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    def disconnect(self) -> None:
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")
    
    def insert_document(self, collection: str, document: Dict[str, Any]) -> Optional[str]:
        """Insert a document into collection."""
        try:
            collection_obj = self.database[collection]
            result = collection_obj.insert_one(document)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Failed to insert document: {e}")
            return None
    
    def find_documents(self, collection: str, query: Dict[str, Any] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Find documents in collection."""
        try:
            collection_obj = self.database[collection]
            cursor = collection_obj.find(query or {}).limit(limit)
            documents = []
            for doc in cursor:
                doc['_id'] = str(doc['_id'])  # Convert ObjectId to string
                documents.append(doc)
            return documents
        except Exception as e:
            logger.error(f"Failed to find documents: {e}")
            return []
    
    def update_document(self, collection: str, query: Dict[str, Any], update: Dict[str, Any]) -> bool:
        """Update document in collection."""
        try:
            collection_obj = self.database[collection]
            result = collection_obj.update_one(query, {"$set": update})
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to update document: {e}")
            return False
    
    def delete_document(self, collection: str, query: Dict[str, Any]) -> bool:
        """Delete document from collection."""
        try:
            collection_obj = self.database[collection]
            result = collection_obj.delete_one(query)
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Failed to delete document: {e}")
            return False
    
    def create_index(self, collection: str, field: str, unique: bool = False) -> bool:
        """Create index on collection field."""
        try:
            collection_obj = self.database[collection]
            collection_obj.create_index([(field, pymongo.ASCENDING)], unique=unique)
            return True
        except Exception as e:
            logger.error(f"Failed to create index: {e}")
            return False


class DatabaseManager:
    """Main database manager that handles multiple database types."""
    
    def __init__(self, config: DatabaseConfig):
        """Initialize database manager."""
        self.config = config
        self.postgres = PostgreSQLManager(config)
        self.mongodb = MongoDBManager()
        self._connected = False
    
    async def connect_all(self) -> None:
        """Connect to all databases."""
        await self.postgres.connect()
        self.mongodb.connect()
        self._connected = True
        logger.info("All database connections established")
    
    async def disconnect_all(self) -> None:
        """Disconnect from all databases."""
        await self.postgres.disconnect()
        self.mongodb.disconnect()
        self._connected = False
        logger.info("All database connections closed")
    
    async def initialize_schema(self) -> bool:
        """Initialize database schema for testing."""
        if not self._connected:
            await self.connect_all()
        
        try:
            # Create PostgreSQL tables
            await self.postgres.create_user_table()
            await self.postgres.create_product_table()
            await self.postgres.create_order_table()
            
            # Create MongoDB indexes
            self.mongodb.create_index("users", "email", unique=True)
            self.mongodb.create_index("products", "category")
            self.mongodb.create_index("orders", "status")
            
            logger.info("Database schema initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize schema: {e}")
            return False
    
    def health_check(self) -> Dict[str, bool]:
        """Check health of all database connections."""
        return {
            "postgresql": self.postgres.pool is not None,
            "mongodb": self.mongodb.client is not None
        } 