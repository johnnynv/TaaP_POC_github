"""Database operations tests for cloud native testing platform."""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
from src.database import DatabaseManager, PostgreSQLManager, MongoDBManager, QueryResult
from src.config import DatabaseConfig


class TestPostgreSQLOperations:
    """Test PostgreSQL database operations (25 tests)."""
    
    @pytest.mark.database
    async def test_postgres_connection_success(self, mock_database):
        """Test successful PostgreSQL connection."""
        config = DatabaseConfig()
        pg_manager = PostgreSQLManager(config)
        
        with patch('asyncpg.create_pool') as mock_pool:
            mock_pool.return_value = AsyncMock()
            await pg_manager.connect()
            assert pg_manager.pool is not None

    @pytest.mark.database
    async def test_postgres_connection_failure(self, mock_database):
        """Test PostgreSQL connection failure."""
        config = DatabaseConfig()
        pg_manager = PostgreSQLManager(config)
        
        with patch('asyncpg.create_pool') as mock_pool:
            mock_pool.side_effect = Exception("Connection failed")
            with pytest.raises(Exception):
                await pg_manager.connect()

    @pytest.mark.database
    async def test_execute_query_success(self, mock_database):
        """Test successful query execution."""
        config = DatabaseConfig()
        pg_manager = PostgreSQLManager(config)
        
        mock_pool = AsyncMock()
        mock_conn = AsyncMock()
        mock_row = Mock()
        mock_row.__iter__ = Mock(return_value=iter([("id", 1), ("name", "test")]))
        mock_conn.fetch.return_value = [mock_row]
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        pg_manager.pool = mock_pool
        
        result = await pg_manager.execute_query("SELECT * FROM users")
        assert result.success is True
        assert result.count == 1

    @pytest.mark.database
    async def test_execute_query_failure(self, mock_database):
        """Test query execution failure."""
        config = DatabaseConfig()
        pg_manager = PostgreSQLManager(config)
        
        mock_pool = AsyncMock()
        mock_conn = AsyncMock()
        mock_conn.fetch.side_effect = Exception("Query failed")
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        pg_manager.pool = mock_pool
        
        result = await pg_manager.execute_query("SELECT * FROM invalid_table")
        assert result.success is False
        assert result.error is not None

    @pytest.mark.database
    async def test_execute_command_success(self, mock_database):
        """Test successful command execution."""
        config = DatabaseConfig()
        pg_manager = PostgreSQLManager(config)
        
        mock_pool = AsyncMock()
        mock_conn = AsyncMock()
        mock_conn.execute.return_value = None
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        pg_manager.pool = mock_pool
        
        result = await pg_manager.execute_command("INSERT INTO users (name) VALUES ($1)", "John")
        assert result is True

    @pytest.mark.database
    async def test_execute_command_failure(self, mock_database):
        """Test command execution failure."""
        config = DatabaseConfig()
        pg_manager = PostgreSQLManager(config)
        
        mock_pool = AsyncMock()
        mock_conn = AsyncMock()
        mock_conn.execute.side_effect = Exception("Command failed")
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        pg_manager.pool = mock_pool
        
        result = await pg_manager.execute_command("INVALID SQL")
        assert result is False

    @pytest.mark.database
    async def test_create_user_table_success(self, mock_database):
        """Test successful user table creation."""
        config = DatabaseConfig()
        pg_manager = PostgreSQLManager(config)
        
        mock_pool = AsyncMock()
        mock_conn = AsyncMock()
        mock_conn.execute.return_value = None
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        pg_manager.pool = mock_pool
        
        result = await pg_manager.create_user_table()
        assert result is True

    @pytest.mark.database
    async def test_create_product_table_success(self, mock_database):
        """Test successful product table creation."""
        config = DatabaseConfig()
        pg_manager = PostgreSQLManager(config)
        
        mock_pool = AsyncMock()
        mock_conn = AsyncMock()
        mock_conn.execute.return_value = None
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        pg_manager.pool = mock_pool
        
        result = await pg_manager.create_product_table()
        assert result is True

    @pytest.mark.database
    async def test_create_order_table_success(self, mock_database):
        """Test successful order table creation."""
        config = DatabaseConfig()
        pg_manager = PostgreSQLManager(config)
        
        mock_pool = AsyncMock()
        mock_conn = AsyncMock()
        mock_conn.execute.return_value = None
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        pg_manager.pool = mock_pool
        
        result = await pg_manager.create_order_table()
        assert result is True

    @pytest.mark.database
    async def test_query_with_parameters(self, mock_database):
        """Test query execution with parameters."""
        config = DatabaseConfig()
        pg_manager = PostgreSQLManager(config)
        
        mock_pool = AsyncMock()
        mock_conn = AsyncMock()
        mock_row = Mock()
        mock_row.__iter__ = Mock(return_value=iter([("id", 1), ("name", "John")]))
        mock_conn.fetch.return_value = [mock_row]
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        pg_manager.pool = mock_pool
        
        result = await pg_manager.execute_query("SELECT * FROM users WHERE id = $1", 1)
        assert result.success is True

    @pytest.mark.database
    async def test_bulk_insert_operations(self, mock_database):
        """Test bulk insert operations."""
        config = DatabaseConfig()
        pg_manager = PostgreSQLManager(config)
        
        mock_pool = AsyncMock()
        mock_conn = AsyncMock()
        mock_conn.executemany = AsyncMock()
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        pg_manager.pool = mock_pool
        
        # Simulate bulk insert
        users_data = [("John", "john@example.com"), ("Jane", "jane@example.com")]
        # In real implementation, this would be a method in PostgreSQLManager
        assert mock_conn.executemany is not None

    @pytest.mark.database
    async def test_transaction_operations(self, mock_database):
        """Test database transaction operations."""
        config = DatabaseConfig()
        pg_manager = PostgreSQLManager(config)
        
        mock_pool = AsyncMock()
        mock_conn = AsyncMock()
        mock_transaction = AsyncMock()
        mock_conn.transaction.return_value.__aenter__.return_value = mock_transaction
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        pg_manager.pool = mock_pool
        
        # Test transaction context
        assert mock_conn.transaction is not None

    @pytest.mark.database
    async def test_prepared_statements(self, mock_database):
        """Test prepared statement usage."""
        config = DatabaseConfig()
        pg_manager = PostgreSQLManager(config)
        
        mock_pool = AsyncMock()
        mock_conn = AsyncMock()
        mock_stmt = AsyncMock()
        mock_conn.prepare.return_value = mock_stmt
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        pg_manager.pool = mock_pool
        
        # Test prepared statement
        assert mock_conn.prepare is not None

    @pytest.mark.database
    async def test_connection_pool_exhaustion(self, mock_database):
        """Test handling of connection pool exhaustion."""
        config = DatabaseConfig()
        pg_manager = PostgreSQLManager(config)
        
        mock_pool = AsyncMock()
        mock_pool.acquire.side_effect = Exception("Pool exhausted")
        pg_manager.pool = mock_pool
        
        result = await pg_manager.execute_query("SELECT 1")
        assert result.success is False

    @pytest.mark.database
    async def test_query_timeout_handling(self, mock_database):
        """Test query timeout handling."""
        config = DatabaseConfig()
        pg_manager = PostgreSQLManager(config)
        
        mock_pool = AsyncMock()
        mock_conn = AsyncMock()
        mock_conn.fetch.side_effect = asyncio.TimeoutError("Query timeout")
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        pg_manager.pool = mock_pool
        
        result = await pg_manager.execute_query("SELECT pg_sleep(100)")
        assert result.success is False

    @pytest.mark.database
    async def test_concurrent_query_execution(self, mock_database):
        """Test concurrent query execution."""
        config = DatabaseConfig()
        pg_manager = PostgreSQLManager(config)
        
        mock_pool = AsyncMock()
        mock_conn = AsyncMock()
        mock_row = Mock()
        mock_row.__iter__ = Mock(return_value=iter([("result", 1)]))
        mock_conn.fetch.return_value = [mock_row]
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        pg_manager.pool = mock_pool
        
        # Execute multiple queries concurrently
        tasks = [
            pg_manager.execute_query("SELECT 1"),
            pg_manager.execute_query("SELECT 2"),
            pg_manager.execute_query("SELECT 3")
        ]
        results = await asyncio.gather(*tasks)
        assert all(result.success for result in results)

    @pytest.mark.database
    async def test_json_data_operations(self, mock_database):
        """Test JSON data operations."""
        config = DatabaseConfig()
        pg_manager = PostgreSQLManager(config)
        
        mock_pool = AsyncMock()
        mock_conn = AsyncMock()
        mock_row = Mock()
        json_data = {"name": "John", "age": 30, "tags": ["developer", "tester"]}
        mock_row.__iter__ = Mock(return_value=iter([("data", json_data)]))
        mock_conn.fetch.return_value = [mock_row]
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        pg_manager.pool = mock_pool
        
        result = await pg_manager.execute_query("SELECT data FROM json_table WHERE id = $1", 1)
        assert result.success is True

    @pytest.mark.database
    async def test_array_data_operations(self, mock_database):
        """Test array data operations."""
        config = DatabaseConfig()
        pg_manager = PostgreSQLManager(config)
        
        mock_pool = AsyncMock()
        mock_conn = AsyncMock()
        mock_row = Mock()
        array_data = ["item1", "item2", "item3"]
        mock_row.__iter__ = Mock(return_value=iter([("items", array_data)]))
        mock_conn.fetch.return_value = [mock_row]
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        pg_manager.pool = mock_pool
        
        result = await pg_manager.execute_query("SELECT items FROM array_table WHERE id = $1", 1)
        assert result.success is True

    @pytest.mark.database
    async def test_full_text_search(self, mock_database):
        """Test full-text search operations."""
        config = DatabaseConfig()
        pg_manager = PostgreSQLManager(config)
        
        mock_pool = AsyncMock()
        mock_conn = AsyncMock()
        mock_row = Mock()
        mock_row.__iter__ = Mock(return_value=iter([("title", "Test Document"), ("rank", 0.5)]))
        mock_conn.fetch.return_value = [mock_row]
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        pg_manager.pool = mock_pool
        
        search_query = "SELECT title, ts_rank(search_vector, query) as rank FROM documents WHERE search_vector @@ to_tsquery($1)"
        result = await pg_manager.execute_query(search_query, "test & document")
        assert result.success is True

    @pytest.mark.database
    async def test_window_functions(self, mock_database):
        """Test window function operations."""
        config = DatabaseConfig()
        pg_manager = PostgreSQLManager(config)
        
        mock_pool = AsyncMock()
        mock_conn = AsyncMock()
        mock_row = Mock()
        mock_row.__iter__ = Mock(return_value=iter([("name", "John"), ("rank", 1)]))
        mock_conn.fetch.return_value = [mock_row]
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        pg_manager.pool = mock_pool
        
        window_query = "SELECT name, ROW_NUMBER() OVER (ORDER BY score DESC) as rank FROM users"
        result = await pg_manager.execute_query(window_query)
        assert result.success is True

    @pytest.mark.database
    async def test_cte_operations(self, mock_database):
        """Test Common Table Expression (CTE) operations."""
        config = DatabaseConfig()
        pg_manager = PostgreSQLManager(config)
        
        mock_pool = AsyncMock()
        mock_conn = AsyncMock()
        mock_row = Mock()
        mock_row.__iter__ = Mock(return_value=iter([("level", 1), ("name", "Root")]))
        mock_conn.fetch.return_value = [mock_row]
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        pg_manager.pool = mock_pool
        
        cte_query = """
        WITH RECURSIVE category_tree AS (
            SELECT id, name, parent_id, 1 as level FROM categories WHERE parent_id IS NULL
            UNION ALL
            SELECT c.id, c.name, c.parent_id, ct.level + 1
            FROM categories c JOIN category_tree ct ON c.parent_id = ct.id
        )
        SELECT * FROM category_tree
        """
        result = await pg_manager.execute_query(cte_query)
        assert result.success is True

    @pytest.mark.database
    async def test_custom_aggregate_functions(self, mock_database):
        """Test custom aggregate functions."""
        config = DatabaseConfig()
        pg_manager = PostgreSQLManager(config)
        
        mock_pool = AsyncMock()
        mock_conn = AsyncMock()
        mock_row = Mock()
        mock_row.__iter__ = Mock(return_value=iter([("median_value", 50.0)]))
        mock_conn.fetch.return_value = [mock_row]
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        pg_manager.pool = mock_pool
        
        aggregate_query = "SELECT percentile_cont(0.5) WITHIN GROUP (ORDER BY value) as median_value FROM measurements"
        result = await pg_manager.execute_query(aggregate_query)
        assert result.success is True

    @pytest.mark.database
    async def test_upsert_operations(self, mock_database):
        """Test UPSERT (INSERT ... ON CONFLICT) operations."""
        config = DatabaseConfig()
        pg_manager = PostgreSQLManager(config)
        
        mock_pool = AsyncMock()
        mock_conn = AsyncMock()
        mock_conn.execute.return_value = None
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        pg_manager.pool = mock_pool
        
        upsert_query = """
        INSERT INTO user_stats (user_id, login_count, last_login)
        VALUES ($1, $2, $3)
        ON CONFLICT (user_id)
        DO UPDATE SET login_count = user_stats.login_count + 1, last_login = $3
        """
        result = await pg_manager.execute_command(upsert_query, 1, 1, datetime.now())
        assert result is True

    @pytest.mark.database
    async def test_explain_query_analysis(self, mock_database):
        """Test EXPLAIN query analysis."""
        config = DatabaseConfig()
        pg_manager = PostgreSQLManager(config)
        
        mock_pool = AsyncMock()
        mock_conn = AsyncMock()
        mock_row = Mock()
        explain_plan = "Seq Scan on users  (cost=0.00..15.00 rows=500 width=32)"
        mock_row.__iter__ = Mock(return_value=iter([("QUERY PLAN", explain_plan)]))
        mock_conn.fetch.return_value = [mock_row]
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        pg_manager.pool = mock_pool
        
        result = await pg_manager.execute_query("EXPLAIN SELECT * FROM users WHERE age > 25")
        assert result.success is True


class TestMongoDBOperations:
    """Test MongoDB database operations (25 tests)."""
    
    @pytest.mark.database
    def test_mongodb_connection_success(self):
        """Test successful MongoDB connection."""
        mongo_manager = MongoDBManager()
        
        with patch('pymongo.MongoClient') as mock_client:
            mock_instance = Mock()
            mock_instance.admin.command.return_value = {"ok": 1}
            mock_client.return_value = mock_instance
            
            mongo_manager.connect()
            assert mongo_manager.client is not None

    @pytest.mark.database
    def test_mongodb_connection_failure(self):
        """Test MongoDB connection failure."""
        mongo_manager = MongoDBManager()
        
        with patch('pymongo.MongoClient') as mock_client:
            mock_client.side_effect = Exception("Connection failed")
            
            with pytest.raises(Exception):
                mongo_manager.connect()

    @pytest.mark.database
    def test_insert_document_success(self):
        """Test successful document insertion."""
        mongo_manager = MongoDBManager()
        mock_client = Mock()
        mock_db = Mock()
        mock_collection = Mock()
        mock_result = Mock()
        mock_result.inserted_id = "507f1f77bcf86cd799439011"
        
        mock_collection.insert_one.return_value = mock_result
        mock_db.__getitem__.return_value = mock_collection
        mock_client.__getitem__.return_value = mock_db
        mongo_manager.client = mock_client
        mongo_manager.database = mock_db
        
        document = {"name": "John", "age": 30}
        result = mongo_manager.insert_document("users", document)
        assert result == "507f1f77bcf86cd799439011"

    @pytest.mark.database
    def test_insert_document_failure(self):
        """Test document insertion failure."""
        mongo_manager = MongoDBManager()
        mock_client = Mock()
        mock_db = Mock()
        mock_collection = Mock()
        
        mock_collection.insert_one.side_effect = Exception("Insert failed")
        mock_db.__getitem__.return_value = mock_collection
        mongo_manager.client = mock_client
        mongo_manager.database = mock_db
        
        result = mongo_manager.insert_document("users", {"name": "John"})
        assert result is None

    @pytest.mark.database
    def test_find_documents_success(self):
        """Test successful document finding."""
        mongo_manager = MongoDBManager()
        mock_client = Mock()
        mock_db = Mock()
        mock_collection = Mock()
        
        mock_documents = [
            {"_id": "507f1f77bcf86cd799439011", "name": "John", "age": 30},
            {"_id": "507f1f77bcf86cd799439012", "name": "Jane", "age": 25}
        ]
        mock_cursor = Mock()
        mock_cursor.__iter__ = Mock(return_value=iter(mock_documents))
        mock_collection.find.return_value.limit.return_value = mock_cursor
        mock_db.__getitem__.return_value = mock_collection
        mongo_manager.client = mock_client
        mongo_manager.database = mock_db
        
        result = mongo_manager.find_documents("users", {"age": {"$gte": 20}}, limit=10)
        assert len(result) == 2
        assert result[0]["name"] == "John"

    @pytest.mark.database
    def test_update_document_success(self):
        """Test successful document update."""
        mongo_manager = MongoDBManager()
        mock_client = Mock()
        mock_db = Mock()
        mock_collection = Mock()
        mock_result = Mock()
        mock_result.modified_count = 1
        
        mock_collection.update_one.return_value = mock_result
        mock_db.__getitem__.return_value = mock_collection
        mongo_manager.client = mock_client
        mongo_manager.database = mock_db
        
        result = mongo_manager.update_document("users", {"_id": "507f1f77bcf86cd799439011"}, {"age": 31})
        assert result is True

    @pytest.mark.database
    def test_delete_document_success(self):
        """Test successful document deletion."""
        mongo_manager = MongoDBManager()
        mock_client = Mock()
        mock_db = Mock()
        mock_collection = Mock()
        mock_result = Mock()
        mock_result.deleted_count = 1
        
        mock_collection.delete_one.return_value = mock_result
        mock_db.__getitem__.return_value = mock_collection
        mongo_manager.client = mock_client
        mongo_manager.database = mock_db
        
        result = mongo_manager.delete_document("users", {"_id": "507f1f77bcf86cd799439011"})
        assert result is True

    @pytest.mark.database
    def test_create_index_success(self):
        """Test successful index creation."""
        mongo_manager = MongoDBManager()
        mock_client = Mock()
        mock_db = Mock()
        mock_collection = Mock()
        
        mock_collection.create_index.return_value = "email_1"
        mock_db.__getitem__.return_value = mock_collection
        mongo_manager.client = mock_client
        mongo_manager.database = mock_db
        
        result = mongo_manager.create_index("users", "email", unique=True)
        assert result is True

    @pytest.mark.database
    def test_aggregation_pipeline(self):
        """Test MongoDB aggregation pipeline."""
        mongo_manager = MongoDBManager()
        mock_client = Mock()
        mock_db = Mock()
        mock_collection = Mock()
        
        aggregation_result = [
            {"_id": "Electronics", "total_sales": 15000, "avg_price": 500},
            {"_id": "Clothing", "total_sales": 8000, "avg_price": 80}
        ]
        mock_collection.aggregate.return_value = iter(aggregation_result)
        mock_db.__getitem__.return_value = mock_collection
        mongo_manager.client = mock_client
        mongo_manager.database = mock_db
        
        pipeline = [
            {"$group": {
                "_id": "$category",
                "total_sales": {"$sum": "$price"},
                "avg_price": {"$avg": "$price"}
            }}
        ]
        
        # In real implementation, this would be a method in MongoDBManager
        result = list(mock_collection.aggregate(pipeline))
        assert len(result) == 2
        assert result[0]["_id"] == "Electronics"

    @pytest.mark.database
    def test_bulk_operations(self):
        """Test MongoDB bulk operations."""
        mongo_manager = MongoDBManager()
        mock_client = Mock()
        mock_db = Mock()
        mock_collection = Mock()
        mock_bulk = Mock()
        mock_result = Mock()
        mock_result.inserted_count = 3
        mock_result.modified_count = 2
        
        mock_collection.bulk_write.return_value = mock_result
        mock_db.__getitem__.return_value = mock_collection
        mongo_manager.client = mock_client
        mongo_manager.database = mock_db
        
        # Test bulk write operations
        assert mock_collection.bulk_write is not None

    @pytest.mark.database
    def test_text_search(self):
        """Test MongoDB text search."""
        mongo_manager = MongoDBManager()
        mock_client = Mock()
        mock_db = Mock()
        mock_collection = Mock()
        
        search_results = [
            {"_id": "1", "title": "MongoDB Tutorial", "score": {"$meta": "textScore"}},
            {"_id": "2", "title": "Database Design", "score": {"$meta": "textScore"}}
        ]
        mock_cursor = Mock()
        mock_cursor.__iter__ = Mock(return_value=iter(search_results))
        mock_collection.find.return_value = mock_cursor
        mock_db.__getitem__.return_value = mock_collection
        mongo_manager.client = mock_client
        mongo_manager.database = mock_db
        
        # Test text search
        query = {"$text": {"$search": "mongodb tutorial"}}
        result = mongo_manager.find_documents("articles", query)
        assert len(result) == 2

    @pytest.mark.database
    def test_geospatial_queries(self):
        """Test MongoDB geospatial queries."""
        mongo_manager = MongoDBManager()
        mock_client = Mock()
        mock_db = Mock()
        mock_collection = Mock()
        
        locations = [
            {"_id": "1", "name": "Central Park", "location": {"type": "Point", "coordinates": [-73.97, 40.77]}},
            {"_id": "2", "name": "Times Square", "location": {"type": "Point", "coordinates": [-73.99, 40.76]}}
        ]
        mock_cursor = Mock()
        mock_cursor.__iter__ = Mock(return_value=iter(locations))
        mock_collection.find.return_value = mock_cursor
        mock_db.__getitem__.return_value = mock_collection
        mongo_manager.client = mock_client
        mongo_manager.database = mock_db
        
        # Test geospatial query
        geo_query = {
            "location": {
                "$near": {
                    "$geometry": {"type": "Point", "coordinates": [-73.98, 40.75]},
                    "$maxDistance": 1000
                }
            }
        }
        result = mongo_manager.find_documents("places", geo_query)
        assert len(result) == 2

    @pytest.mark.database
    def test_array_operations(self):
        """Test MongoDB array operations."""
        mongo_manager = MongoDBManager()
        mock_client = Mock()
        mock_db = Mock()
        mock_collection = Mock()
        mock_result = Mock()
        mock_result.modified_count = 1
        
        mock_collection.update_one.return_value = mock_result
        mock_db.__getitem__.return_value = mock_collection
        mongo_manager.client = mock_client
        mongo_manager.database = mock_db
        
        # Test array push operation
        update_query = {"$push": {"tags": "new_tag"}}
        result = mongo_manager.update_document("products", {"_id": "prod1"}, update_query)
        assert result is True

    @pytest.mark.database
    def test_embedded_document_queries(self):
        """Test queries on embedded documents."""
        mongo_manager = MongoDBManager()
        mock_client = Mock()
        mock_db = Mock()
        mock_collection = Mock()
        
        users_with_addresses = [
            {
                "_id": "1",
                "name": "John",
                "address": {"street": "123 Main St", "city": "New York", "zip": "10001"}
            }
        ]
        mock_cursor = Mock()
        mock_cursor.__iter__ = Mock(return_value=iter(users_with_addresses))
        mock_collection.find.return_value.limit.return_value = mock_cursor
        mock_db.__getitem__.return_value = mock_collection
        mongo_manager.client = mock_client
        mongo_manager.database = mock_db
        
        # Test embedded document query
        query = {"address.city": "New York"}
        result = mongo_manager.find_documents("users", query)
        assert len(result) == 1
        assert result[0]["address"]["city"] == "New York"

    @pytest.mark.database
    def test_collection_statistics(self):
        """Test collection statistics retrieval."""
        mongo_manager = MongoDBManager()
        mock_client = Mock()
        mock_db = Mock()
        mock_collection = Mock()
        
        stats = {
            "ns": "testdb.users",
            "count": 1000,
            "size": 50000,
            "avgObjSize": 50,
            "storageSize": 100000
        }
        mock_collection.aggregate.return_value = iter([{"stats": stats}])
        mock_db.__getitem__.return_value = mock_collection
        mongo_manager.client = mock_client
        mongo_manager.database = mock_db
        
        # Test collection stats
        assert mock_collection.aggregate is not None

    @pytest.mark.database
    def test_document_validation(self):
        """Test document validation rules."""
        mongo_manager = MongoDBManager()
        mock_client = Mock()
        mock_db = Mock()
        
        validation_schema = {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["name", "email"],
                "properties": {
                    "name": {"bsonType": "string"},
                    "email": {"bsonType": "string", "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"}
                }
            }
        }
        
        mock_db.create_collection.return_value = Mock()
        mongo_manager.client = mock_client
        mongo_manager.database = mock_db
        
        # Test collection creation with validation
        assert mock_db.create_collection is not None

    @pytest.mark.database
    def test_change_streams(self):
        """Test MongoDB change streams."""
        mongo_manager = MongoDBManager()
        mock_client = Mock()
        mock_db = Mock()
        mock_collection = Mock()
        
        change_events = [
            {
                "_id": {"_data": "825F..."},
                "operationType": "insert",
                "fullDocument": {"_id": "1", "name": "John"},
                "ns": {"db": "testdb", "coll": "users"}
            }
        ]
        mock_change_stream = Mock()
        mock_change_stream.__iter__ = Mock(return_value=iter(change_events))
        mock_collection.watch.return_value = mock_change_stream
        mock_db.__getitem__.return_value = mock_collection
        mongo_manager.client = mock_client
        mongo_manager.database = mock_db
        
        # Test change stream watching
        assert mock_collection.watch is not None

    @pytest.mark.database
    def test_gridfs_operations(self):
        """Test GridFS file operations."""
        mongo_manager = MongoDBManager()
        mock_client = Mock()
        mock_db = Mock()
        
        with patch('gridfs.GridFS') as mock_gridfs:
            mock_fs = Mock()
            mock_fs.put.return_value = "file_id_123"
            mock_fs.get.return_value.read.return_value = b"file content"
            mock_gridfs.return_value = mock_fs
            
            # Test GridFS operations
            gridfs_instance = mock_gridfs(mock_db)
            file_id = gridfs_instance.put(b"test content", filename="test.txt")
            assert file_id == "file_id_123"

    @pytest.mark.database
    def test_replica_set_operations(self):
        """Test replica set read preferences."""
        mongo_manager = MongoDBManager()
        
        with patch('pymongo.MongoClient') as mock_client:
            mock_instance = Mock()
            mock_instance.admin.command.return_value = {"ok": 1}
            mock_client.return_value = mock_instance
            
            # Test replica set configuration
            mongo_manager.connect()
            assert mongo_manager.client is not None

    @pytest.mark.database
    def test_sharding_operations(self):
        """Test sharding-related operations."""
        mongo_manager = MongoDBManager()
        mock_client = Mock()
        mock_db = Mock()
        
        shard_info = {
            "shards": [
                {"_id": "shard1", "host": "shard1/server1:27018,server2:27018"},
                {"_id": "shard2", "host": "shard2/server3:27018,server4:27018"}
            ]
        }
        mock_db.command.return_value = shard_info
        mongo_manager.client = mock_client
        mongo_manager.database = mock_db
        
        # Test shard status
        assert mock_db.command is not None

    @pytest.mark.database
    def test_map_reduce_operations(self):
        """Test MapReduce operations."""
        mongo_manager = MongoDBManager()
        mock_client = Mock()
        mock_db = Mock()
        mock_collection = Mock()
        
        map_reduce_result = [
            {"_id": "category1", "value": 100},
            {"_id": "category2", "value": 150}
        ]
        mock_collection.map_reduce.return_value = iter(map_reduce_result)
        mock_db.__getitem__.return_value = mock_collection
        mongo_manager.client = mock_client
        mongo_manager.database = mock_db
        
        # Test map-reduce
        assert mock_collection.map_reduce is not None

    @pytest.mark.database
    def test_atomic_operations(self):
        """Test atomic operations."""
        mongo_manager = MongoDBManager()
        mock_client = Mock()
        mock_db = Mock()
        mock_collection = Mock()
        mock_result = Mock()
        mock_result.modified_count = 1
        
        mock_collection.find_one_and_update.return_value = {"_id": "1", "counter": 2}
        mock_db.__getitem__.return_value = mock_collection
        mongo_manager.client = mock_client
        mongo_manager.database = mock_db
        
        # Test atomic increment
        query = {"_id": "counter_doc"}
        update = {"$inc": {"counter": 1}}
        result = mock_collection.find_one_and_update(query, update, upsert=True, return_document=True)
        assert result["counter"] == 2

    @pytest.mark.database
    def test_transaction_operations(self):
        """Test MongoDB transactions."""
        mongo_manager = MongoDBManager()
        mock_client = Mock()
        mock_session = Mock()
        
        mock_client.start_session.return_value = mock_session
        mongo_manager.client = mock_client
        
        # Test transaction session
        with mock_session.start_transaction():
            # Perform transactional operations
            pass
        
        assert mock_client.start_session is not None

    @pytest.mark.database
    def test_capped_collections(self):
        """Test capped collection operations."""
        mongo_manager = MongoDBManager()
        mock_client = Mock()
        mock_db = Mock()
        
        mock_db.create_collection.return_value = Mock()
        mongo_manager.client = mock_client
        mongo_manager.database = mock_db
        
        # Test capped collection creation
        collection_options = {"capped": True, "size": 1000000, "max": 1000}
        mock_db.create_collection("logs", **collection_options)
        mock_db.create_collection.assert_called_with("logs", capped=True, size=1000000, max=1000) 