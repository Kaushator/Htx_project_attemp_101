#!/usr/bin/env python3
"""
Performance test for Phase 2.1 Cache Implementation
Testing time-to-insight ≤ 10 seconds goal
"""
import asyncio
import aiohttp
import time
from typing import Dict, List

BASE_URL = "http://127.0.0.1:8004/api/v1"

async def test_endpoint(session: aiohttp.ClientSession, endpoint: str, name: str) -> Dict:
    """Test single endpoint performance"""
    start_time = time.time()
    
    try:
        async with session.get(f"{BASE_URL}{endpoint}") as response:
            if response.status == 200:
                data = await response.json()
                end_time = time.time()
                return {
                    "endpoint": endpoint,
                    "name": name,
                    "status": "success",
                    "response_time": round(end_time - start_time, 3),
                    "cached": data.get("cached", False) if isinstance(data, dict) else False
                }
            else:
                return {
                    "endpoint": endpoint, 
                    "name": name,
                    "status": "error",
                    "response_time": round(time.time() - start_time, 3),
                    "error": f"HTTP {response.status}"
                }
    except Exception as e:
        return {
            "endpoint": endpoint,
            "name": name, 
            "status": "error",
            "response_time": round(time.time() - start_time, 3),
            "error": str(e)
        }

async def performance_test():
    """Run comprehensive performance test"""
    print("🚀 HTX Project Performance Test - Phase 2.1 Cache Implementation")
    print("=" * 70)
    
    endpoints = [
        ("/health/", "Health Check"),
        ("/trades/", "List Trades"),
        ("/trades/summary", "Trade Stats (Cached)"),
        ("/pnl/summary", "PnL Summary (Cached)"),
        ("/pnl/daily", "Daily PnL"),
        ("/cashflow/", "Cash Flow"),
        ("/htx/status", "HTX Status"),
        ("/files/", "File List"),
    ]
    
    async with aiohttp.ClientSession() as session:
        # First run - cold cache
        print("\n🔥 Cold Cache Test (First Request)")
        print("-" * 40)
        
        cold_results = []
        for endpoint, name in endpoints:
            result = await test_endpoint(session, endpoint, name)
            cold_results.append(result)
            status_icon = "✅" if result["status"] == "success" else "❌"
            print(f"{status_icon} {name:20} {result['response_time']:6.3f}s")
        
        # Second run - warm cache
        print("\n🔥 Warm Cache Test (Second Request)")
        print("-" * 40)
        
        warm_results = []
        for endpoint, name in endpoints:
            result = await test_endpoint(session, endpoint, name)
            warm_results.append(result)
            status_icon = "✅" if result["status"] == "success" else "❌"
            cache_icon = "🎯" if result.get("cached") else "🐌"
            print(f"{status_icon}{cache_icon} {name:20} {result['response_time']:6.3f}s")
        
        # Analysis
        print("\n📊 Performance Analysis")
        print("-" * 40)
        
        successful_cold = [r for r in cold_results if r["status"] == "success"]
        successful_warm = [r for r in warm_results if r["status"] == "success"]
        
        if successful_cold:
            avg_cold = sum(r["response_time"] for r in successful_cold) / len(successful_cold)
            max_cold = max(r["response_time"] for r in successful_cold)
            print(f"Cold Cache Average: {avg_cold:.3f}s")
            print(f"Cold Cache Max:     {max_cold:.3f}s")
        
        if successful_warm:
            avg_warm = sum(r["response_time"] for r in successful_warm) / len(successful_warm)
            max_warm = max(r["response_time"] for r in successful_warm)
            print(f"Warm Cache Average: {avg_warm:.3f}s")
            print(f"Warm Cache Max:     {max_warm:.3f}s")
            
            if successful_cold:
                improvement = ((avg_cold - avg_warm) / avg_cold) * 100
                print(f"Cache Improvement:  {improvement:.1f}%")
        
        # Time-to-insight goal check
        print("\n🎯 Time-to-Insight Goal: ≤ 10 seconds")
        print("-" * 40)
        
        insight_endpoints = [r for r in warm_results if "summary" in r["endpoint"].lower() or "pnl" in r["endpoint"].lower()]
        if insight_endpoints:
            total_insight_time = sum(r["response_time"] for r in insight_endpoints if r["status"] == "success")
            goal_met = total_insight_time <= 10.0
            status_icon = "✅" if goal_met else "❌"
            print(f"{status_icon} Total insight time: {total_insight_time:.3f}s (Goal: ≤10s)")
        
        print("\n" + "=" * 70)

if __name__ == "__main__":
    asyncio.run(performance_test())
