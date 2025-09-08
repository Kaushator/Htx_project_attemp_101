"""
Performance Testing and Bottleneck Analysis for GCP Integration

This module provides comprehensive performance testing tools and bottleneck
analysis for the HTX trading platform's GCP integration.
"""

import asyncio
import time
import logging
import psutil
import statistics
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from contextlib import asynccontextmanager

import httpx
import pandas as pd
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.config import settings
from app.services.gcp import GCPServices, setup_gcp_services

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics data structure"""
    operation_name: str
    start_time: datetime
    end_time: datetime
    duration_ms: float
    success: bool
    error_message: Optional[str] = None
    memory_usage_mb: Optional[float] = None
    cpu_usage_percent: Optional[float] = None


@dataclass
class LoadTestResults:
    """Load test results data structure"""
    test_name: str
    concurrent_users: int
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_response_time_ms: float
    min_response_time_ms: float
    max_response_time_ms: float
    p95_response_time_ms: float
    p99_response_time_ms: float
    throughput_rps: float
    error_rate_percent: float
    memory_peak_mb: float
    cpu_peak_percent: float


class PerformanceMonitor:
    """Performance monitoring and metrics collection"""
    
    def __init__(self):
        self.metrics: List[PerformanceMetrics] = []
        self.system_metrics: List[Dict[str, Any]] = []
        
    @asynccontextmanager
    async def measure_operation(self, operation_name: str):
        """Context manager to measure operation performance"""
        start_time = datetime.utcnow()
        start_memory = psutil.virtual_memory().used / 1024 / 1024  # MB
        start_cpu = psutil.cpu_percent()
        
        success = True
        error_message = None
        
        try:
            yield
        except Exception as e:
            success = False
            error_message = str(e)
            raise
        finally:
            end_time = datetime.utcnow()
            end_memory = psutil.virtual_memory().used / 1024 / 1024  # MB
            end_cpu = psutil.cpu_percent()
            
            duration_ms = (end_time - start_time).total_seconds() * 1000
            
            metric = PerformanceMetrics(
                operation_name=operation_name,
                start_time=start_time,
                end_time=end_time,
                duration_ms=duration_ms,
                success=success,
                error_message=error_message,
                memory_usage_mb=end_memory - start_memory,
                cpu_usage_percent=end_cpu - start_cpu
            )
            
            self.metrics.append(metric)
            logger.info(f"Operation {operation_name}: {duration_ms:.2f}ms, Success: {success}")
    
    def get_summary_stats(self, operation_name: Optional[str] = None) -> Dict[str, Any]:
        """Get summary statistics for operations"""
        filtered_metrics = self.metrics
        if operation_name:
            filtered_metrics = [m for m in self.metrics if m.operation_name == operation_name]
        
        if not filtered_metrics:
            return {}
        
        durations = [m.duration_ms for m in filtered_metrics if m.success]
        success_count = sum(1 for m in filtered_metrics if m.success)
        total_count = len(filtered_metrics)
        
        return {
            "operation_name": operation_name or "all_operations",
            "total_operations": total_count,
            "successful_operations": success_count,
            "success_rate": success_count / total_count * 100,
            "average_duration_ms": statistics.mean(durations) if durations else 0,
            "median_duration_ms": statistics.median(durations) if durations else 0,
            "min_duration_ms": min(durations) if durations else 0,
            "max_duration_ms": max(durations) if durations else 0,
            "p95_duration_ms": statistics.quantiles(durations, n=20)[18] if len(durations) > 20 else (max(durations) if durations else 0),
            "p99_duration_ms": statistics.quantiles(durations, n=100)[98] if len(durations) > 100 else (max(durations) if durations else 0)
        }


class GCPPerformanceTester:
    """Performance testing for GCP services"""
    
    def __init__(self, gcp_services: GCPServices):
        self.gcp_services = gcp_services
        self.monitor = PerformanceMonitor()
    
    async def test_storage_performance(self, 
                                     file_sizes: List[int] = [1024, 10240, 102400],  # 1KB, 10KB, 100KB
                                     concurrent_uploads: int = 5) -> Dict[str, Any]:
        """Test Cloud Storage performance with different file sizes"""
        results = {}
        
        for file_size in file_sizes:
            test_name = f"storage_upload_{file_size}B"
            
            # Create test data
            test_data = b"x" * file_size
            
            # Test concurrent uploads
            tasks = []
            for i in range(concurrent_uploads):
                blob_name = f"perf_test_{file_size}_{i}_{int(time.time())}.txt"
                task = self._test_single_upload(test_data, blob_name, test_name)
                tasks.append(task)
            
            await asyncio.gather(*tasks, return_exceptions=True)
            
            # Get statistics for this test
            results[test_name] = self.monitor.get_summary_stats(test_name)
        
        return results
    
    async def _test_single_upload(self, data: bytes, blob_name: str, operation_name: str):
        """Test single file upload"""
        try:
            async with self.monitor.measure_operation(operation_name):
                from io import BytesIO
                file_obj = BytesIO(data)
                await self.gcp_services.storage.upload_file(
                    file_path=file_obj,
                    blob_name=blob_name,
                    content_type="text/plain"
                )
        except Exception as e:
            logger.error(f"Upload failed for {blob_name}: {e}")
    
    async def test_pubsub_performance(self,
                                    message_counts: List[int] = [10, 100, 1000],
                                    concurrent_publishers: int = 5) -> Dict[str, Any]:
        """Test Pub/Sub performance with different message volumes"""
        results = {}
        topic_name = f"perf_test_{int(time.time())}"
        
        # Create test topic
        await self.gcp_services.pubsub.create_topic(topic_name)
        
        for message_count in message_counts:
            test_name = f"pubsub_publish_{message_count}_messages"
            
            # Test concurrent publishing
            tasks = []
            messages_per_publisher = message_count // concurrent_publishers
            
            for publisher_id in range(concurrent_publishers):
                task = self._test_pubsub_publisher(
                    topic_name, 
                    messages_per_publisher, 
                    publisher_id, 
                    test_name
                )
                tasks.append(task)
            
            await asyncio.gather(*tasks, return_exceptions=True)
            
            results[test_name] = self.monitor.get_summary_stats(test_name)
        
        return results
    
    async def _test_pubsub_publisher(self, topic_name: str, message_count: int, 
                                   publisher_id: int, operation_name: str):
        """Test single publisher performance"""
        for i in range(message_count):
            try:
                async with self.monitor.measure_operation(operation_name):
                    await self.gcp_services.pubsub.publish_message(
                        topic_name=topic_name,
                        data={
                            "publisher_id": publisher_id,
                            "message_id": i,
                            "timestamp": datetime.utcnow().isoformat(),
                            "test_data": "x" * 100  # 100 bytes of test data
                        }
                    )
            except Exception as e:
                logger.error(f"Publish failed for message {i}: {e}")
    
    async def test_secret_manager_performance(self,
                                            secret_counts: List[int] = [10, 50, 100]) -> Dict[str, Any]:
        """Test Secret Manager performance"""
        results = {}
        
        for secret_count in secret_counts:
            test_name = f"secret_manager_{secret_count}_secrets"
            
            # Test secret creation
            for i in range(secret_count):
                secret_name = f"perf_test_secret_{i}_{int(time.time())}"
                try:
                    async with self.monitor.measure_operation(f"{test_name}_create"):
                        await self.gcp_services.secret_manager.create_secret(
                            secret_name=secret_name,
                            secret_value=f"test-secret-value-{i}"
                        )
                except Exception as e:
                    logger.error(f"Secret creation failed for {secret_name}: {e}")
            
            # Test secret retrieval
            for i in range(secret_count):
                secret_name = f"perf_test_secret_{i}_{int(time.time())}"
                try:
                    async with self.monitor.measure_operation(f"{test_name}_get"):
                        await self.gcp_services.secret_manager.get_secret(secret_name)
                except Exception as e:
                    logger.error(f"Secret retrieval failed for {secret_name}: {e}")
            
            results[f"{test_name}_create"] = self.monitor.get_summary_stats(f"{test_name}_create")
            results[f"{test_name}_get"] = self.monitor.get_summary_stats(f"{test_name}_get")
        
        return results


class APILoadTester:
    """Load testing for GCP API endpoints"""
    
    def __init__(self, base_url: str = "http://localhost:8004"):
        self.base_url = base_url
        self.monitor = PerformanceMonitor()
    
    async def run_load_test(self,
                          endpoint: str,
                          method: str = "GET",
                          payload: Optional[Dict[str, Any]] = None,
                          concurrent_users: int = 10,
                          requests_per_user: int = 10,
                          ramp_up_time: float = 1.0) -> LoadTestResults:
        """Run load test against an API endpoint"""
        
        start_time = datetime.utcnow()
        total_requests = concurrent_users * requests_per_user
        
        # Create semaphore to control concurrency
        semaphore = asyncio.Semaphore(concurrent_users)
        
        # Track system metrics
        initial_memory = psutil.virtual_memory().used / 1024 / 1024
        initial_cpu = psutil.cpu_percent()
        
        # Create tasks with ramp-up
        tasks = []
        for user_id in range(concurrent_users):
            # Stagger user start times
            delay = (user_id * ramp_up_time) / concurrent_users
            task = self._simulate_user(
                semaphore, endpoint, method, payload, 
                requests_per_user, user_id, delay
            )
            tasks.append(task)
        
        # Execute all tasks
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = datetime.utcnow()
        
        # Calculate metrics
        successful_requests = sum(1 for r in results if isinstance(r, list) and all(req.get("success", False) for req in r))
        failed_requests = total_requests - successful_requests
        
        # Get response times from successful requests
        response_times = []
        for result in results:
            if isinstance(result, list):
                response_times.extend([req["duration_ms"] for req in result if req.get("success")])
        
        # Calculate performance metrics
        test_duration = (end_time - start_time).total_seconds()
        throughput = successful_requests / test_duration if test_duration > 0 else 0
        
        peak_memory = psutil.virtual_memory().used / 1024 / 1024
        peak_cpu = psutil.cpu_percent()
        
        return LoadTestResults(
            test_name=f"{method}_{endpoint}",
            concurrent_users=concurrent_users,
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            average_response_time_ms=statistics.mean(response_times) if response_times else 0,
            min_response_time_ms=min(response_times) if response_times else 0,
            max_response_time_ms=max(response_times) if response_times else 0,
            p95_response_time_ms=statistics.quantiles(response_times, n=20)[18] if len(response_times) > 20 else 0,
            p99_response_time_ms=statistics.quantiles(response_times, n=100)[98] if len(response_times) > 100 else 0,
            throughput_rps=throughput,
            error_rate_percent=(failed_requests / total_requests * 100) if total_requests > 0 else 0,
            memory_peak_mb=peak_memory - initial_memory,
            cpu_peak_percent=peak_cpu - initial_cpu
        )
    
    async def _simulate_user(self,
                           semaphore: asyncio.Semaphore,
                           endpoint: str,
                           method: str,
                           payload: Optional[Dict[str, Any]],
                           requests_count: int,
                           user_id: int,
                           delay: float) -> List[Dict[str, Any]]:
        """Simulate a single user making requests"""
        
        # Wait for ramp-up delay
        await asyncio.sleep(delay)
        
        results = []
        
        async with httpx.AsyncClient() as client:
            for request_id in range(requests_count):
                async with semaphore:
                    result = await self._make_request(
                        client, endpoint, method, payload, f"user_{user_id}_req_{request_id}"
                    )
                    results.append(result)
                    
                    # Small delay between requests from same user
                    await asyncio.sleep(0.1)
        
        return results
    
    async def _make_request(self,
                          client: httpx.AsyncClient,
                          endpoint: str,
                          method: str,
                          payload: Optional[Dict[str, Any]],
                          request_id: str) -> Dict[str, Any]:
        """Make a single HTTP request and measure performance"""
        
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            if method.upper() == "GET":
                response = await client.get(url, timeout=30.0)
            elif method.upper() == "POST":
                response = await client.post(url, json=payload, timeout=30.0)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000
            
            return {
                "request_id": request_id,
                "success": response.status_code < 400,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
                "response_size": len(response.content) if response.content else 0
            }
            
        except Exception as e:
            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000
            
            return {
                "request_id": request_id,
                "success": False,
                "error": str(e),
                "duration_ms": duration_ms,
                "response_size": 0
            }


class BottleneckAnalyzer:
    """Analyze performance bottlenecks in GCP integration"""
    
    def __init__(self):
        self.analysis_results: Dict[str, Any] = {}
    
    def analyze_performance_metrics(self, metrics: List[PerformanceMetrics]) -> Dict[str, Any]:
        """Analyze performance metrics to identify bottlenecks"""
        
        # Group metrics by operation
        operation_groups = {}
        for metric in metrics:
            if metric.operation_name not in operation_groups:
                operation_groups[metric.operation_name] = []
            operation_groups[metric.operation_name].append(metric)
        
        bottlenecks = []
        
        for operation_name, operation_metrics in operation_groups.items():
            analysis = self._analyze_operation(operation_name, operation_metrics)
            
            # Identify potential bottlenecks
            if analysis["average_duration_ms"] > 1000:  # > 1 second
                bottlenecks.append({
                    "operation": operation_name,
                    "issue": "High latency",
                    "severity": "high" if analysis["average_duration_ms"] > 5000 else "medium",
                    "average_duration_ms": analysis["average_duration_ms"],
                    "recommendation": "Optimize network calls or implement caching"
                })
            
            if analysis["error_rate"] > 5:  # > 5% error rate
                bottlenecks.append({
                    "operation": operation_name,
                    "issue": "High error rate",
                    "severity": "high" if analysis["error_rate"] > 10 else "medium",
                    "error_rate": analysis["error_rate"],
                    "recommendation": "Implement better error handling and retry logic"
                })
            
            if analysis["memory_usage_peak_mb"] > 100:  # > 100MB memory usage
                bottlenecks.append({
                    "operation": operation_name,
                    "issue": "High memory usage",
                    "severity": "medium",
                    "memory_peak_mb": analysis["memory_usage_peak_mb"],
                    "recommendation": "Optimize data structures or implement streaming"
                })
        
        return {
            "operation_analysis": {op: self._analyze_operation(op, metrics) for op, metrics in operation_groups.items()},
            "bottlenecks": bottlenecks,
            "recommendations": self._generate_recommendations(bottlenecks)
        }
    
    def _analyze_operation(self, operation_name: str, metrics: List[PerformanceMetrics]) -> Dict[str, Any]:
        """Analyze metrics for a specific operation"""
        
        successful_metrics = [m for m in metrics if m.success]
        failed_metrics = [m for m in metrics if not m.success]
        
        if not metrics:
            return {}
        
        durations = [m.duration_ms for m in successful_metrics]
        memory_usage = [m.memory_usage_mb for m in metrics if m.memory_usage_mb is not None]
        
        return {
            "operation_name": operation_name,
            "total_executions": len(metrics),
            "successful_executions": len(successful_metrics),
            "failed_executions": len(failed_metrics),
            "error_rate": (len(failed_metrics) / len(metrics)) * 100,
            "average_duration_ms": statistics.mean(durations) if durations else 0,
            "p95_duration_ms": statistics.quantiles(durations, n=20)[18] if len(durations) > 20 else 0,
            "memory_usage_peak_mb": max(memory_usage) if memory_usage else 0,
            "common_errors": [m.error_message for m in failed_metrics if m.error_message]
        }
    
    def _generate_recommendations(self, bottlenecks: List[Dict[str, Any]]) -> List[str]:
        """Generate performance improvement recommendations"""
        
        recommendations = []
        
        high_latency_ops = [b for b in bottlenecks if b["issue"] == "High latency"]
        if high_latency_ops:
            recommendations.append(
                "Consider implementing connection pooling and keep-alive for GCP clients"
            )
            recommendations.append(
                "Implement caching for frequently accessed data (secrets, small files)"
            )
        
        high_error_ops = [b for b in bottlenecks if b["issue"] == "High error rate"]
        if high_error_ops:
            recommendations.append(
                "Implement exponential backoff retry logic with jitter"
            )
            recommendations.append(
                "Add circuit breaker pattern for failing services"
            )
        
        memory_intensive_ops = [b for b in bottlenecks if b["issue"] == "High memory usage"]
        if memory_intensive_ops:
            recommendations.append(
                "Implement streaming for large file operations"
            )
            recommendations.append(
                "Consider batch processing for bulk operations"
            )
        
        return recommendations


# Main performance testing runner
async def run_comprehensive_performance_test():
    """Run comprehensive performance testing suite"""
    
    logger.info("Starting comprehensive GCP performance testing")
    
    # Initialize GCP services
    gcp_services = await setup_gcp_services(settings)
    
    if not gcp_services.is_configured:
        logger.warning("GCP services not configured, skipping performance tests")
        return
    
    # Initialize testers
    gcp_tester = GCPPerformanceTester(gcp_services)
    api_tester = APILoadTester()
    analyzer = BottleneckAnalyzer()
    
    results = {}
    
    try:
        # Test GCP service performance
        if gcp_services.storage.is_available:
            logger.info("Testing Cloud Storage performance")
            results["storage"] = await gcp_tester.test_storage_performance()
        
        if gcp_services.pubsub.is_available:
            logger.info("Testing Pub/Sub performance")
            results["pubsub"] = await gcp_tester.test_pubsub_performance()
        
        if gcp_services.secret_manager.is_available:
            logger.info("Testing Secret Manager performance")
            results["secret_manager"] = await gcp_tester.test_secret_manager_performance()
        
        # Test API endpoints
        logger.info("Testing GCP API endpoints")
        api_results = []
        
        # Test health endpoint
        health_result = await api_tester.run_load_test("/api/v1/gcp/health", concurrent_users=5)
        api_results.append(health_result)
        
        # Analyze bottlenecks
        logger.info("Analyzing performance bottlenecks")
        all_metrics = []
        all_metrics.extend(gcp_tester.monitor.metrics)
        all_metrics.extend(api_tester.monitor.metrics)
        
        bottleneck_analysis = analyzer.analyze_performance_metrics(all_metrics)
        
        # Compile final results
        final_results = {
            "gcp_services": results,
            "api_endpoints": [result.__dict__ for result in api_results],
            "bottleneck_analysis": bottleneck_analysis,
            "test_summary": {
                "total_operations": len(all_metrics),
                "successful_operations": sum(1 for m in all_metrics if m.success),
                "test_duration_minutes": 5,  # Approximate
                "recommendations": bottleneck_analysis.get("recommendations", [])
            }
        }
        
        logger.info("Performance testing completed successfully")
        return final_results
        
    except Exception as e:
        logger.error(f"Performance testing failed: {e}")
        raise
    
    finally:
        # Cleanup
        await gcp_services.close_all()


if __name__ == "__main__":
    asyncio.run(run_comprehensive_performance_test())