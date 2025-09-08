# Performance Testing Scenarios for HTX Trading Platform

## Overview

Comprehensive performance testing framework targeting high-volume data processing (100k+ records), parallel operations, and system scalability validation for the HTX Trading Platform.

## Performance Targets

```yaml
performance_targets:
  file_processing:
    small_files_1mb: "< 5 seconds"
    large_files_50mb: "< 2 minutes"
    massive_100k_records: "< 5 minutes"
    
  concurrent_operations:
    parallel_uploads_10: "< 15 seconds"
    parallel_uploads_50: "< 60 seconds"
    api_requests: "500/minute sustained"
    
  analytics_performance:
    basic_pnl_1k: "< 500ms"
    complex_100k: "< 30 seconds"
    risk_metrics: "< 10 seconds"
    
  resource_constraints:
    max_memory: "< 2GB for 100k records"
    cpu_usage: "< 80% sustained"
```

## Test Categories

### 1. Large File Processing Tests

#### 1.1 High-Volume Record Processing
```python
# test_large_file_performance.py
import pytest
import time
import psutil
from httpx import AsyncClient
from app.main import app

class TestLargeFilePerformance:
    
    def create_large_csv(self, num_records: int, filename: str):
        """Generate large CSV with trading records"""
        csv_path = f"test_data/{filename}"
        
        with open(csv_path, 'w') as f:
            f.write("date,symbol,side,quantity,price,fee\n")
            
            for i in range(num_records):
                date = f"2024-01-{(i % 28) + 1:02d}T{(i % 24):02d}:00:00Z"
                symbol = ["BTCUSDT", "ETHUSDT", "ADAUSDT"][i % 3]
                side = "buy" if i % 2 == 0 else "sell"
                quantity = round(0.001 + (i % 1000) * 0.001, 6)
                price = 30000 + (i % 40000)
                fee = round(price * quantity * 0.001, 4)
                
                f.write(f"{date},{symbol},{side},{quantity},{price},{fee}\n")
        
        return csv_path
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_100k_records_processing(self):
        """Process 100,000 trading records performance test"""
        test_file = self.create_large_csv(100000, "trades_100k.csv")
        
        # Monitor resources
        process = psutil.Process()
        initial_memory = process.memory_info().rss / (1024 * 1024)
        
        start_time = time.time()
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            with open(test_file, 'rb') as f:
                files = {"file": ("trades_100k.csv", f, "text/csv")}
                response = await client.post("/api/v1/files/upload", files=files)
        
        processing_time = time.time() - start_time
        final_memory = process.memory_info().rss / (1024 * 1024)
        memory_used = final_memory - initial_memory
        
        # Validate results
        assert response.status_code == 200
        assert response.json()["records_processed"] == 100000
        
        # Performance requirements
        assert processing_time < 300  # Under 5 minutes
        assert memory_used < 1000     # Under 1GB additional memory
        
        records_per_second = 100000 / processing_time
        print(f"Performance: {records_per_second:.0f} records/sec, {memory_used:.1f}MB used")
        
        # Cleanup
        import os
        os.remove(test_file)
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_memory_efficiency_chunked(self):
        """Test memory-efficient chunked processing"""
        test_file = self.create_large_csv(200000, "trades_200k.csv")
        
        process = psutil.Process()
        memory_before = process.memory_info().rss / (1024 * 1024)
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            with open(test_file, 'rb') as f:
                files = {"file": ("trades_200k.csv", f, "text/csv")}
                response = await client.post(
                    "/api/v1/files/upload?chunk_size=5000", 
                    files=files
                )
        
        memory_after = process.memory_info().rss / (1024 * 1024)
        memory_used = memory_after - memory_before
        
        assert response.status_code == 200
        assert response.json()["records_processed"] == 200000
        assert memory_used < 500  # Chunked processing should be memory efficient
        
        import os
        os.remove(test_file)
```

### 2. Concurrent Operations Testing

#### 2.1 Parallel File Upload Performance
```python
# test_concurrent_performance.py
import pytest
import asyncio
import time
from httpx import AsyncClient
from app.main import app

class TestConcurrentOperations:
    
    def create_test_csv(self, records: int, file_id: str):
        """Create test CSV content"""
        content = "date,symbol,side,quantity,price,fee\n"
        for i in range(records):
            content += f"2024-01-01,BTCUSDT,buy,{0.1+i*0.001},{30000+i},0.1\n"
        return content.encode()
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_10_concurrent_uploads(self):
        """Test 10 simultaneous file uploads"""
        async def upload_file(file_id):
            csv_content = self.create_test_csv(1000, file_id)
            async with AsyncClient(app=app, base_url="http://test") as client:
                files = {"file": (f"test_{file_id}.csv", csv_content, "text/csv")}
                start = time.time()
                response = await client.post("/api/v1/files/upload", files=files)
                return {
                    "success": response.status_code == 200,
                    "time": time.time() - start,
                    "records": response.json().get("records_processed", 0) if response.status_code == 200 else 0
                }
        
        # Execute concurrent uploads
        start_time = time.time()
        tasks = [upload_file(i) for i in range(10)]
        results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time
        
        successful = [r for r in results if r["success"]]
        
        assert len(successful) >= 8  # 80% success rate
        assert total_time < 30       # Complete within 30 seconds
        assert all(r["records"] == 1000 for r in successful)
        
        print(f"Concurrent uploads: {len(successful)}/10 successful in {total_time:.1f}s")
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_mixed_size_uploads(self):
        """Test concurrent uploads of varying file sizes"""
        file_configs = [
            ("small", 100), ("small", 100), ("small", 100),
            ("medium", 5000), ("medium", 5000),
            ("large", 20000)
        ]
        
        async def upload_mixed_file(size_type, records, file_id):
            csv_content = self.create_test_csv(records, file_id)
            async with AsyncClient(app=app, base_url="http://test") as client:
                files = {"file": (f"{size_type}_{file_id}.csv", csv_content, "text/csv")}
                response = await client.post("/api/v1/files/upload", files=files)
                return {
                    "type": size_type,
                    "success": response.status_code == 200,
                    "records": records
                }
        
        tasks = [upload_mixed_file(size_type, records, i) 
                for i, (size_type, records) in enumerate(file_configs)]
        
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time
        
        successful = [r for r in results if r["success"]]
        
        assert len(successful) >= 5  # Most uploads succeed
        assert total_time < 60       # Complete within 1 minute
        
        print(f"Mixed uploads: {len(successful)}/6 successful in {total_time:.1f}s")
```

### 3. Analytics Performance Testing

#### 3.1 P&L Calculation Performance
```python
# test_analytics_performance.py
import pytest
import time
from httpx import AsyncClient
from app.main import app

class TestAnalyticsPerformance:
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_pnl_calculation_scalability(self):
        """Test P&L calculation performance with increasing data sizes"""
        data_sizes = [1000, 10000, 50000]
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            for size in data_sizes:
                start_time = time.time()
                response = await client.get(f"/api/v1/advanced-pnl/summary?days=30&limit={size}")
                processing_time = time.time() - start_time
                
                if response.status_code == 200:
                    # Performance targets by data size
                    if size <= 1000:
                        assert processing_time < 1.0    # 1K records: <1s
                    elif size <= 10000:
                        assert processing_time < 10.0   # 10K records: <10s
                    else:
                        assert processing_time < 30.0   # 50K records: <30s
                    
                    print(f"P&L {size} records: {processing_time:.2f}s")
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_comprehensive_analytics_performance(self):
        """Test complex analytics calculation performance"""
        start_time = time.time()
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/v1/advanced-pnl/comprehensive?days=365")
        
        processing_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            assert "basic_pnl" in data
            assert "risk_metrics" in data
            assert processing_time < 60  # Annual analytics under 1 minute
            
            print(f"Comprehensive analytics: {processing_time:.2f}s")
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_concurrent_analytics_load(self):
        """Test concurrent analytics requests performance"""
        endpoints = [
            "/api/v1/advanced-pnl/summary?days=30",
            "/api/v1/insights/dashboard",
            "/api/v1/insights/top-symbols?limit=10"
        ]
        
        async def call_endpoint(endpoint):
            async with AsyncClient(app=app, base_url="http://test") as client:
                start = time.time()
                response = await client.get(endpoint)
                return {
                    "endpoint": endpoint,
                    "success": response.status_code == 200,
                    "time": time.time() - start
                }
        
        # Run concurrent analytics requests
        tasks = [call_endpoint(ep) for ep in endpoints for _ in range(3)]  # 3x each
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time
        
        successful = [r for r in results if r["success"]]
        
        assert len(successful) >= len(tasks) * 0.8  # 80% success rate
        assert total_time < 30  # All concurrent requests under 30s
        
        print(f"Concurrent analytics: {len(successful)}/{len(tasks)} in {total_time:.1f}s")
```

### 4. Database Performance Testing

#### 4.1 Bulk Operations Performance
```python
# test_database_performance.py
import pytest
import time
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.trade import Trade
from app.db.session import get_async_session
from decimal import Decimal
from datetime import datetime, timedelta

class TestDatabasePerformance:
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_bulk_insert_performance(self):
        """Test bulk database insert performance"""
        record_counts = [1000, 10000, 50000]
        
        async with get_async_session() as session:
            for count in record_counts:
                # Generate test data
                trades = []
                for i in range(count):
                    trade = Trade(
                        symbol="BTCUSDT" if i % 2 == 0 else "ETHUSDT",
                        side="buy" if i % 2 == 0 else "sell",
                        quantity=Decimal(f"{0.001 + (i % 1000) * 0.001:.6f}"),
                        price=Decimal(f"{30000 + (i % 40000)}"),
                        fee=Decimal("0.1"),
                        time=datetime.utcnow() - timedelta(minutes=i)
                    )
                    trades.append(trade)
                
                # Bulk insert with timing
                start_time = time.time()
                session.add_all(trades)
                await session.commit()
                insert_time = time.time() - start_time
                
                records_per_second = count / insert_time
                
                # Performance targets
                if count == 1000:
                    assert insert_time < 10
                elif count == 10000:
                    assert insert_time < 60
                elif count == 50000:
                    assert insert_time < 300
                
                print(f"Bulk insert {count} records: {insert_time:.1f}s ({records_per_second:.0f}/sec)")
                
                # Cleanup
                await session.execute("DELETE FROM trades")
                await session.commit()
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_query_performance(self):
        """Test database query performance with large dataset"""
        async with get_async_session() as session:
            # Create test dataset
            trades = []
            for i in range(25000):
                trade = Trade(
                    symbol=["BTCUSDT", "ETHUSDT", "ADAUSDT"][i % 3],
                    side="buy" if i % 2 == 0 else "sell",
                    quantity=Decimal(f"{0.1 + (i % 100) * 0.01:.4f}"),
                    price=Decimal(f"{1000 + (i % 50000)}"),
                    fee=Decimal("0.1"),
                    time=datetime.utcnow() - timedelta(hours=i//100)
                )
                trades.append(trade)
            
            session.add_all(trades)
            await session.commit()
            
            # Test query patterns
            queries = [
                ("Count all", "SELECT COUNT(*) FROM trades"),
                ("Symbol filter", "SELECT * FROM trades WHERE symbol = 'BTCUSDT' LIMIT 1000"),
                ("Aggregation", "SELECT symbol, SUM(quantity), AVG(price) FROM trades GROUP BY symbol")
            ]
            
            for name, query in queries:
                start_time = time.time()
                await session.execute(query)
                query_time = time.time() - start_time
                
                assert query_time < 5  # All queries under 5 seconds
                print(f"Query '{name}': {query_time:.3f}s")
            
            # Cleanup
            await session.execute("DELETE FROM trades")
            await session.commit()
```

## Performance Test Execution

### Automated Test Runner
```bash
#!/bin/bash
# run_performance_tests.sh

echo "⚡ HTX Performance Test Suite"
echo "============================="

export TESTING=true
export DATABASE_URL="sqlite+aiosqlite:///./test_perf.db"

mkdir -p test_data reports

echo "🔄 Large File Processing Tests..."
pytest -m "performance and large_files" tests/performance/ -v

echo "🔄 Concurrent Operations Tests..."
pytest -m "performance and concurrent" tests/performance/ -v

echo "📊 Analytics Performance Tests..."
pytest -m "performance and analytics" tests/performance/ -v

echo "💾 Database Performance Tests..."
pytest -m "performance and database" tests/performance/ -v

echo "📋 Generating Report..."
pytest --html=reports/performance.html -m "performance" tests/performance/

rm -rf test_data/
echo "✅ Performance testing complete!"
```

### Performance Monitoring
```python
# performance_monitor.py
import psutil
import time
import json

class PerformanceMonitor:
    def __init__(self):
        self.start_time = time.time()
        self.initial_memory = psutil.Process().memory_info().rss
        self.samples = []
    
    def sample(self, operation_name):
        """Record performance sample"""
        current_time = time.time()
        current_memory = psutil.Process().memory_info().rss
        
        self.samples.append({
            'timestamp': current_time - self.start_time,
            'operation': operation_name,
            'memory_mb': current_memory / (1024 * 1024),
            'memory_delta_mb': (current_memory - self.initial_memory) / (1024 * 1024),
            'cpu_percent': psutil.cpu_percent()
        })
    
    def report(self):
        """Generate performance report"""
        return {
            'total_duration': time.time() - self.start_time,
            'peak_memory_mb': max(s['memory_mb'] for s in self.samples),
            'avg_cpu_percent': sum(s['cpu_percent'] for s in self.samples) / len(self.samples),
            'samples': self.samples
        }
```

This performance testing framework ensures the HTX Trading Platform can handle production-scale workloads with 100k+ records, concurrent operations, and complex analytics while maintaining acceptable response times and resource usage.