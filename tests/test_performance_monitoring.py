"""Performance and monitoring tests for cloud native testing platform."""

import pytest
import time
import threading
import asyncio
import psutil
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta


class TestPerformanceMetrics:
    """Test performance metrics collection and analysis (15 tests)."""
    
    @pytest.mark.performance
    def test_execution_time_measurement(self):
        """Test execution time measurement."""
        def sample_function():
            time.sleep(0.1)
            return "completed"
        
        start_time = time.time()
        result = sample_function()
        end_time = time.time()
        execution_time = end_time - start_time
        
        assert result == "completed"
        assert 0.09 < execution_time < 0.15  # Allow some tolerance

    @pytest.mark.performance
    def test_memory_usage_monitoring(self):
        """Test memory usage monitoring."""
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        
        # Allocate some memory
        large_list = [i for i in range(100000)]
        current_memory = process.memory_info().rss
        
        assert current_memory > initial_memory
        assert len(large_list) == 100000
        
        # Clean up
        del large_list

    @pytest.mark.performance
    def test_cpu_usage_monitoring(self):
        """Test CPU usage monitoring."""
        def cpu_intensive_task():
            # Simulate CPU-intensive work
            total = 0
            for i in range(1000000):
                total += i * i
            return total
        
        # Measure CPU usage during task
        process = psutil.Process()
        initial_cpu = process.cpu_percent()
        
        result = cpu_intensive_task()
        
        # Get CPU usage after some time
        time.sleep(0.1)
        final_cpu = process.cpu_percent()
        
        assert result > 0
        assert isinstance(final_cpu, float)

    @pytest.mark.performance
    def test_disk_io_monitoring(self):
        """Test disk I/O monitoring."""
        import tempfile
        import os
        
        # Create temporary file for I/O testing
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_filename = temp_file.name
        
        try:
            # Monitor disk I/O
            process = psutil.Process()
            initial_io = process.io_counters()
            
            # Perform file operations
            test_data = b"test data " * 1000
            with open(temp_filename, 'wb') as f:
                f.write(test_data)
            
            with open(temp_filename, 'rb') as f:
                read_data = f.read()
            
            final_io = process.io_counters()
            
            assert read_data == test_data
            assert final_io.write_bytes >= initial_io.write_bytes
            assert final_io.read_bytes >= initial_io.read_bytes
            
        finally:
            os.unlink(temp_filename)

    @pytest.mark.performance
    def test_network_latency_simulation(self):
        """Test network latency simulation."""
        def simulate_network_call(latency_ms=100):
            time.sleep(latency_ms / 1000.0)
            return {"status": "success", "data": "response"}
        
        start_time = time.perf_counter()
        response = simulate_network_call(50)
        end_time = time.perf_counter()
        
        latency = (end_time - start_time) * 1000  # Convert to milliseconds
        
        assert response["status"] == "success"
        assert 45 < latency < 55  # Allow tolerance

    @pytest.mark.performance
    def test_throughput_measurement(self):
        """Test throughput measurement."""
        def process_items(items):
            processed = []
            for item in items:
                # Simulate processing
                processed.append(item * 2)
            return processed
        
        items = list(range(10000))
        start_time = time.perf_counter()
        
        processed_items = process_items(items)
        
        end_time = time.perf_counter()
        processing_time = end_time - start_time
        throughput = len(items) / processing_time  # items per second
        
        assert len(processed_items) == len(items)
        assert throughput > 0
        assert processed_items[100] == 200  # 100 * 2

    @pytest.mark.performance
    def test_concurrent_performance(self):
        """Test concurrent performance measurement."""
        def worker_task(task_id, duration=0.1):
            start = time.perf_counter()
            time.sleep(duration)
            end = time.perf_counter()
            return {"task_id": task_id, "duration": end - start}
        
        num_threads = 5
        task_duration = 0.1
        
        start_time = time.perf_counter()
        
        threads = []
        results = []
        
        def thread_wrapper(task_id):
            result = worker_task(task_id, task_duration)
            results.append(result)
        
        for i in range(num_threads):
            thread = threading.Thread(target=thread_wrapper, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        end_time = time.perf_counter()
        total_time = end_time - start_time
        
        assert len(results) == num_threads
        # Concurrent execution should be faster than sequential
        assert total_time < (num_threads * task_duration * 1.5)

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_async_performance(self):
        """Test asynchronous performance measurement."""
        async def async_task(task_id, delay=0.1):
            start = time.perf_counter()
            await asyncio.sleep(delay)
            end = time.perf_counter()
            return {"task_id": task_id, "duration": end - start}
        
        num_tasks = 10
        task_delay = 0.1
        
        start_time = time.perf_counter()
        
        # Run tasks concurrently
        tasks = [async_task(i, task_delay) for i in range(num_tasks)]
        results = await asyncio.gather(*tasks)
        
        end_time = time.perf_counter()
        total_time = end_time - start_time
        
        assert len(results) == num_tasks
        # Async execution should be much faster than sequential
        assert total_time < (num_tasks * task_delay * 0.5)

    @pytest.mark.performance
    def test_cache_performance(self):
        """Test cache performance measurement."""
        import functools
        
        call_count = 0
        
        @functools.lru_cache(maxsize=100)
        def expensive_computation(n):
            nonlocal call_count
            call_count += 1
            time.sleep(0.01)  # Simulate expensive operation
            return n * n
        
        # First calls - should be slow
        start_time = time.perf_counter()
        results1 = [expensive_computation(i) for i in range(10)]
        first_duration = time.perf_counter() - start_time
        
        # Reset call count for cache hits
        first_call_count = call_count
        
        # Second calls - should be fast (cached)
        start_time = time.perf_counter()
        results2 = [expensive_computation(i) for i in range(10)]
        second_duration = time.perf_counter() - start_time
        
        assert results1 == results2
        assert call_count == first_call_count  # No additional calls for cached results
        assert second_duration < first_duration * 0.1  # Cache should be much faster

    @pytest.mark.performance
    def test_database_query_performance(self):
        """Test database query performance simulation."""
        class MockDatabase:
            def __init__(self):
                self.query_times = []
            
            def execute_query(self, query, use_index=True):
                # Simulate query execution time
                base_time = 0.001  # 1ms base time
                if "WHERE" in query and use_index:
                    query_time = base_time * 1  # Fast with index
                elif "WHERE" in query and not use_index:
                    query_time = base_time * 100  # Slow without index
                else:
                    query_time = base_time * 10  # Medium for full scan
                
                time.sleep(query_time)
                self.query_times.append(query_time)
                return [{"id": 1, "name": "test"}]
        
        db = MockDatabase()
        
        # Test indexed query
        start = time.perf_counter()
        result1 = db.execute_query("SELECT * FROM users WHERE id = 1", use_index=True)
        indexed_time = time.perf_counter() - start
        
        # Test non-indexed query
        start = time.perf_counter()
        result2 = db.execute_query("SELECT * FROM users WHERE name = 'test'", use_index=False)
        non_indexed_time = time.perf_counter() - start
        
        assert len(result1) == 1
        assert len(result2) == 1
        assert non_indexed_time > indexed_time * 50  # Non-indexed should be much slower

    @pytest.mark.performance
    def test_api_response_time(self):
        """Test API response time measurement."""
        def simulate_api_call(endpoint, method="GET"):
            # Simulate different response times for different endpoints
            response_times = {
                "/users": 0.05,
                "/products": 0.1,
                "/orders": 0.2,
                "/analytics": 0.5
            }
            
            base_time = response_times.get(endpoint, 0.1)
            if method == "POST":
                base_time *= 1.5  # POST operations typically slower
            
            time.sleep(base_time)
            
            return {
                "status": 200,
                "data": f"Response from {endpoint}",
                "timestamp": time.time()
            }
        
        endpoints = ["/users", "/products", "/orders", "/analytics"]
        response_times = {}
        
        for endpoint in endpoints:
            start = time.perf_counter()
            response = simulate_api_call(endpoint)
            end = time.perf_counter()
            
            response_time = (end - start) * 1000  # Convert to milliseconds
            response_times[endpoint] = response_time
            
            assert response["status"] == 200
        
        # Verify response time ordering
        assert response_times["/users"] < response_times["/products"]
        assert response_times["/products"] < response_times["/orders"]
        assert response_times["/orders"] < response_times["/analytics"]

    @pytest.mark.performance
    def test_load_testing_simulation(self):
        """Test load testing simulation."""
        import queue
        import threading
        
        def simulate_user_request():
            # Simulate user request processing
            time.sleep(0.01)  # 10ms processing time
            return {"user_id": threading.current_thread().ident, "success": True}
        
        def worker(request_queue, results_queue):
            while True:
                try:
                    request = request_queue.get(timeout=1)
                    if request is None:
                        break
                    result = simulate_user_request()
                    results_queue.put(result)
                    request_queue.task_done()
                except queue.Empty:
                    break
        
        # Setup load test
        num_requests = 100
        num_workers = 10
        
        request_queue = queue.Queue()
        results_queue = queue.Queue()
        
        # Add requests to queue
        for i in range(num_requests):
            request_queue.put(f"request_{i}")
        
        # Start workers
        workers = []
        start_time = time.perf_counter()
        
        for _ in range(num_workers):
            worker_thread = threading.Thread(target=worker, args=(request_queue, results_queue))
            worker_thread.start()
            workers.append(worker_thread)
        
        # Wait for completion
        request_queue.join()
        
        # Stop workers
        for _ in range(num_workers):
            request_queue.put(None)
        
        for worker_thread in workers:
            worker_thread.join()
        
        end_time = time.perf_counter()
        total_time = end_time - start_time
        
        # Collect results
        results = []
        while not results_queue.empty():
            results.append(results_queue.get())
        
        requests_per_second = len(results) / total_time
        
        assert len(results) == num_requests
        assert requests_per_second > 0
        # With 10 workers, should be faster than sequential processing
        assert total_time < (num_requests * 0.01 * 0.5)

    @pytest.mark.performance
    def test_memory_leak_detection(self):
        """Test memory leak detection."""
        import gc
        
        def potentially_leaky_function():
            # Create some objects that might leak
            data = []
            for i in range(1000):
                data.append({"id": i, "data": "x" * 100})
            return data
        
        # Measure memory before
        gc.collect()  # Force garbage collection
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        
        # Run function multiple times
        for _ in range(10):
            result = potentially_leaky_function()
            del result  # Explicitly delete
        
        # Force garbage collection
        gc.collect()
        
        # Measure memory after
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be minimal after garbage collection
        # Allow some increase for Python overhead
        max_allowed_increase = 10 * 1024 * 1024  # 10MB
        assert memory_increase < max_allowed_increase

    @pytest.mark.performance
    def test_scaling_performance(self):
        """Test performance scaling with different data sizes."""
        def process_data(data_size):
            # Create data of specified size
            data = list(range(data_size))
            
            # Process data (simulate O(n) algorithm)
            start = time.perf_counter()
            processed = [x * 2 for x in data]
            end = time.perf_counter()
            
            return end - start, len(processed)
        
        data_sizes = [1000, 2000, 4000, 8000]
        performance_results = {}
        
        for size in data_sizes:
            duration, count = process_data(size)
            performance_results[size] = duration
            assert count == size
        
        # Check that performance scales roughly linearly (O(n))
        # Double the data size should roughly double the time
        ratio_2k_1k = performance_results[2000] / performance_results[1000]
        ratio_4k_2k = performance_results[4000] / performance_results[2000]
        
        # Allow some variance, but should be roughly 2x
        assert 1.5 < ratio_2k_1k < 3.0
        assert 1.5 < ratio_4k_2k < 3.0

    @pytest.mark.performance
    def test_resource_cleanup_performance(self):
        """Test resource cleanup performance."""
        import tempfile
        import os
        
        class ResourceManager:
            def __init__(self):
                self.temp_files = []
                self.open_files = []
            
            def create_temp_file(self):
                temp_file = tempfile.NamedTemporaryFile(delete=False)
                self.temp_files.append(temp_file.name)
                self.open_files.append(temp_file)
                return temp_file
            
            def cleanup(self):
                start = time.perf_counter()
                
                # Close open files
                for file_obj in self.open_files:
                    if not file_obj.closed:
                        file_obj.close()
                
                # Delete temp files
                for filename in self.temp_files:
                    try:
                        os.unlink(filename)
                    except FileNotFoundError:
                        pass
                
                self.temp_files.clear()
                self.open_files.clear()
                
                end = time.perf_counter()
                return end - start
        
        # Create and cleanup many resources
        manager = ResourceManager()
        
        # Create many temporary files
        for _ in range(100):
            temp_file = manager.create_temp_file()
            temp_file.write(b"test data")
        
        # Measure cleanup time
        cleanup_time = manager.cleanup()
        
        # Cleanup should be fast even for many resources
        assert cleanup_time < 1.0  # Should complete within 1 second
        assert len(manager.temp_files) == 0
        assert len(manager.open_files) == 0 

    @pytest.mark.performance
    def test_memory_pool_performance(self):
        """Test memory pool allocation performance."""
        import gc
        
        class SimpleMemoryPool:
            def __init__(self, pool_size=1000):
                self.pool = [bytearray(1024) for _ in range(pool_size)]
                self.available = list(range(pool_size))
                self.in_use = set()
            
            def allocate(self):
                if self.available:
                    idx = self.available.pop()
                    self.in_use.add(idx)
                    return self.pool[idx]
                return None
            
            def deallocate(self, buffer):
                for idx, pool_buffer in enumerate(self.pool):
                    if pool_buffer is buffer and idx in self.in_use:
                        self.in_use.remove(idx)
                        self.available.append(idx)
                        break
        
        pool = SimpleMemoryPool(100)
        
        # Test allocation performance
        start = time.perf_counter()
        buffers = []
        for _ in range(50):
            buf = pool.allocate()
            if buf:
                buffers.append(buf)
        allocation_time = time.perf_counter() - start
        
        # Test deallocation performance
        start = time.perf_counter()
        for buf in buffers:
            pool.deallocate(buf)
        deallocation_time = time.perf_counter() - start
        
        assert len(buffers) == 50
        assert allocation_time < 0.1  # Should be very fast
        assert deallocation_time < 0.1

    @pytest.mark.performance
    def test_string_concatenation_performance(self):
        """Test different string concatenation methods performance."""
        test_strings = [f"string_{i}" for i in range(1000)]
        
        # Method 1: += operator
        start = time.perf_counter()
        result1 = ""
        for s in test_strings:
            result1 += s
        method1_time = time.perf_counter() - start
        
        # Method 2: join
        start = time.perf_counter()
        result2 = "".join(test_strings)
        method2_time = time.perf_counter() - start
        
        # Method 3: list append + join
        start = time.perf_counter()
        parts = []
        for s in test_strings:
            parts.append(s)
        result3 = "".join(parts)
        method3_time = time.perf_counter() - start
        
        assert result1 == result2 == result3
        assert method2_time < method1_time  # join should be faster
        assert method3_time < method1_time

    @pytest.mark.performance
    def test_dictionary_access_performance(self):
        """Test dictionary vs list access performance."""
        # Create test data
        size = 10000
        test_dict = {f"key_{i}": f"value_{i}" for i in range(size)}
        test_list = [(f"key_{i}", f"value_{i}") for i in range(size)]
        
        search_keys = [f"key_{i}" for i in range(0, size, 100)]
        
        # Dictionary lookup
        start = time.perf_counter()
        dict_results = []
        for key in search_keys:
            if key in test_dict:
                dict_results.append(test_dict[key])
        dict_time = time.perf_counter() - start
        
        # List search
        start = time.perf_counter()
        list_results = []
        for key in search_keys:
            for k, v in test_list:
                if k == key:
                    list_results.append(v)
                    break
        list_time = time.perf_counter() - start
        
        assert len(dict_results) == len(list_results) == len(search_keys)
        assert dict_time < list_time  # Dictionary should be much faster

    @pytest.mark.performance
    def test_file_io_buffering_performance(self):
        """Test file I/O with different buffer sizes."""
        import tempfile
        import os
        
        # Create test data
        test_data = b"x" * (1024 * 1024)  # 1MB of data
        
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_filename = temp_file.name
        
        try:
            buffer_sizes = [1024, 8192, 65536]  # 1KB, 8KB, 64KB
            write_times = {}
            read_times = {}
            
            for buffer_size in buffer_sizes:
                # Test write performance
                start = time.perf_counter()
                with open(temp_filename, 'wb', buffering=buffer_size) as f:
                    f.write(test_data)
                write_times[buffer_size] = time.perf_counter() - start
                
                # Test read performance
                start = time.perf_counter()
                with open(temp_filename, 'rb', buffering=buffer_size) as f:
                    read_data = f.read()
                read_times[buffer_size] = time.perf_counter() - start
                
                assert read_data == test_data
            
            # Larger buffers should generally be faster for large files
            assert len(write_times) == len(read_times) == 3
            
        finally:
            os.unlink(temp_filename)

    @pytest.mark.performance
    def test_regex_compilation_caching(self):
        """Test regex compilation vs pre-compiled regex performance."""
        import re
        
        test_strings = [f"test_string_{i}@example.com" for i in range(1000)]
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        # Test without pre-compilation
        start = time.perf_counter()
        matches1 = []
        for s in test_strings:
            if re.match(pattern, s):
                matches1.append(s)
        no_cache_time = time.perf_counter() - start
        
        # Test with pre-compiled regex
        compiled_pattern = re.compile(pattern)
        start = time.perf_counter()
        matches2 = []
        for s in test_strings:
            if compiled_pattern.match(s):
                matches2.append(s)
        cached_time = time.perf_counter() - start
        
        assert len(matches1) == len(matches2) == len(test_strings)
        assert cached_time < no_cache_time  # Pre-compiled should be faster

    @pytest.mark.performance
    def test_set_vs_list_membership(self):
        """Test set vs list membership testing performance."""
        size = 10000
        test_data = list(range(size))
        test_set = set(test_data)
        test_list = test_data.copy()
        
        search_items = list(range(0, size, 100))
        
        # Set membership testing
        start = time.perf_counter()
        set_found = []
        for item in search_items:
            if item in test_set:
                set_found.append(item)
        set_time = time.perf_counter() - start
        
        # List membership testing
        start = time.perf_counter()
        list_found = []
        for item in search_items:
            if item in test_list:
                list_found.append(item)
        list_time = time.perf_counter() - start
        
        assert len(set_found) == len(list_found) == len(search_items)
        assert set_time < list_time  # Set should be much faster

    @pytest.mark.performance
    def test_generator_vs_list_comprehension(self):
        """Test generator vs list comprehension memory and performance."""
        import sys
        
        size = 100000
        
        # List comprehension
        start = time.perf_counter()
        list_result = [x * 2 for x in range(size)]
        list_time = time.perf_counter() - start
        list_memory = sys.getsizeof(list_result)
        
        # Generator expression
        start = time.perf_counter()
        gen_result = (x * 2 for x in range(size))
        gen_time = time.perf_counter() - start
        gen_memory = sys.getsizeof(gen_result)
        
        # Convert generator to list for comparison
        start = time.perf_counter()
        gen_list = list(gen_result)
        gen_convert_time = time.perf_counter() - start
        
        assert len(list_result) == len(gen_list) == size
        assert list_result == gen_list
        assert gen_memory < list_memory  # Generator should use less memory
        assert gen_time < list_time  # Generator creation should be faster

    @pytest.mark.performance
    def test_sorting_algorithm_performance(self):
        """Test different sorting approaches performance."""
        import random
        
        # Create test data
        size = 10000
        original_data = list(range(size))
        random.shuffle(original_data)
        
        # Built-in sort
        data1 = original_data.copy()
        start = time.perf_counter()
        data1.sort()
        builtin_time = time.perf_counter() - start
        
        # Sorted function
        data2 = original_data.copy()
        start = time.perf_counter()
        sorted_data = sorted(data2)
        sorted_time = time.perf_counter() - start
        
        # Custom key function sort
        data3 = [(x, str(x)) for x in original_data]
        start = time.perf_counter()
        data3.sort(key=lambda x: x[0])
        key_sort_time = time.perf_counter() - start
        
        assert data1 == sorted_data == list(range(size))
        assert [x[0] for x in data3] == list(range(size))
        # Built-in sort should generally be fastest
        assert builtin_time < sorted_time + 0.1  # Allow some tolerance 