"""
Performance Benchmarking Framework

Provides tools and utilities for benchmarking autonomous development system performance.
"""

import time
import statistics
import json
import psutil
import os
from pathlib import Path
from typing import Dict, List, Any, Callable, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
from contextlib import contextmanager


@dataclass
class BenchmarkResult:
    """Result of a single benchmark run"""

    name: str
    duration_seconds: float
    memory_mb: float
    cpu_percent: float
    iterations: int = 1
    success: bool = True
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class BenchmarkSuite:
    """Collection of benchmark results"""

    suite_name: str
    results: List[BenchmarkResult] = field(default_factory=list)
    total_duration: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def add_result(self, result: BenchmarkResult):
        """Add a benchmark result to the suite"""
        self.results.append(result)
        self.total_duration += result.duration_seconds

    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics"""
        durations = [r.duration_seconds for r in self.results if r.success]

        return {
            "suite_name": self.suite_name,
            "total_benchmarks": len(self.results),
            "successful": sum(1 for r in self.results if r.success),
            "failed": sum(1 for r in self.results if not r.success),
            "total_duration": self.total_duration,
            "avg_duration": statistics.mean(durations) if durations else 0,
            "min_duration": min(durations) if durations else 0,
            "max_duration": max(durations) if durations else 0,
            "median_duration": statistics.median(durations) if durations else 0,
            "avg_memory_mb": statistics.mean(
                [r.memory_mb for r in self.results if r.success]
            )
            if durations
            else 0,
            "timestamp": self.timestamp,
        }

    def save_to_file(self, filepath: Path):
        """Save benchmark results to JSON file"""
        data = {
            "suite": asdict(self),
            "summary": self.get_summary(),
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    def print_summary(self):
        """Print formatted summary"""
        summary = self.get_summary()

        print(f"\n{'='*60}")
        print(f"Benchmark Suite: {self.suite_name}")
        print(f"{'='*60}")
        print(f"Total Benchmarks: {summary['total_benchmarks']}")
        print(f"  Successful: {summary['successful']}")
        print(f"  Failed: {summary['failed']}")
        print(f"\nTiming:")
        print(f"  Total Duration: {summary['total_duration']:.2f}s")
        print(f"  Average Duration: {summary['avg_duration']:.3f}s")
        print(f"  Median Duration: {summary['median_duration']:.3f}s")
        print(f"  Min Duration: {summary['min_duration']:.3f}s")
        print(f"  Max Duration: {summary['max_duration']:.3f}s")
        print(f"\nResources:")
        print(f"  Average Memory: {summary['avg_memory_mb']:.2f} MB")
        print(f"{'='*60}\n")

        # Print individual results
        print("\nIndividual Results:")
        print(f"{'Name':<40} {'Duration':<12} {'Memory':<12} {'Status'}")
        print("-" * 80)

        for result in self.results:
            status = "✓" if result.success else "✗"
            print(
                f"{result.name:<40} "
                f"{result.duration_seconds:>10.3f}s "
                f"{result.memory_mb:>10.2f}MB "
                f"{status}"
            )


class PerformanceBenchmark:
    """Main benchmarking class"""

    def __init__(
        self,
        suite_name: str = "Performance Benchmark",
        output_dir: Optional[Path] = None,
    ):
        self.suite_name = suite_name
        self.suite = BenchmarkSuite(suite_name=suite_name)
        self.output_dir = output_dir or Path("tests/performance/results")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Process for memory tracking
        self.process = psutil.Process(os.getpid())

    @contextmanager
    def measure(
        self,
        name: str,
        iterations: int = 1,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Context manager for measuring performance"""

        # Reset memory baseline
        self.process.memory_info()

        # Start measurements
        start_time = time.perf_counter()
        start_memory = self.process.memory_info().rss / (1024 * 1024)  # MB
        cpu_percent_start = psutil.cpu_percent(interval=None)

        result = BenchmarkResult(
            name=name,
            duration_seconds=0.0,
            memory_mb=0.0,
            cpu_percent=0.0,
            iterations=iterations,
            metadata=metadata or {},
        )

        try:
            yield result
        except Exception as e:
            result.success = False
            result.error = str(e)
            raise
        finally:
            # End measurements
            end_time = time.perf_counter()
            end_memory = self.process.memory_info().rss / (1024 * 1024)  # MB
            cpu_percent_end = psutil.cpu_percent(interval=None)

            result.duration_seconds = end_time - start_time
            result.memory_mb = end_memory - start_memory
            result.cpu_percent = (cpu_percent_start + cpu_percent_end) / 2

            self.suite.add_result(result)

    def benchmark(
        self,
        func: Callable,
        name: Optional[str] = None,
        iterations: int = 1,
        warmup: int = 0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> BenchmarkResult:
        """Benchmark a function"""

        benchmark_name = name or func.__name__

        # Warmup runs
        for _ in range(warmup):
            func()

        # Actual benchmark
        with self.measure(
            name=benchmark_name, iterations=iterations, metadata=metadata
        ) as result:
            if iterations == 1:
                func()
            else:
                # Run multiple iterations
                for _ in range(iterations):
                    func()

        return result

    def compare(
        self,
        functions: Dict[str, Callable],
        iterations: int = 1,
        warmup: int = 0,
    ) -> Dict[str, BenchmarkResult]:
        """Compare multiple functions"""

        results = {}

        for name, func in functions.items():
            result = self.benchmark(
                func=func, name=name, iterations=iterations, warmup=warmup
            )
            results[name] = result

        # Print comparison
        print(f"\n{'='*60}")
        print("Benchmark Comparison")
        print(f"{'='*60}")
        print(f"{'Function':<30} {'Duration':<15} {'Relative'}")
        print("-" * 60)

        # Sort by duration
        sorted_results = sorted(
            results.items(), key=lambda x: x[1].duration_seconds
        )

        baseline = sorted_results[0][1].duration_seconds

        for name, result in sorted_results:
            relative = result.duration_seconds / baseline
            print(
                f"{name:<30} {result.duration_seconds:>12.3f}s "
                f"{relative:>10.2f}x"
            )

        print(f"{'='*60}\n")

        return results

    def save_results(self, filename: Optional[str] = None):
        """Save benchmark results to file"""

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"benchmark_{timestamp}.json"

        filepath = self.output_dir / filename
        self.suite.save_to_file(filepath)

        print(f"Results saved to: {filepath}")

    def print_summary(self):
        """Print benchmark summary"""
        self.suite.print_summary()


class MemoryProfiler:
    """Memory profiling utilities"""

    @staticmethod
    @contextmanager
    def track_memory():
        """Track memory usage in a context"""

        process = psutil.Process(os.getpid())
        start_memory = process.memory_info().rss / (1024 * 1024)  # MB

        memory_stats = {"start_mb": start_memory, "peak_mb": start_memory}

        try:
            yield memory_stats
        finally:
            end_memory = process.memory_info().rss / (1024 * 1024)
            memory_stats["end_mb"] = end_memory
            memory_stats["delta_mb"] = end_memory - start_memory

    @staticmethod
    def get_memory_usage() -> Dict[str, float]:
        """Get current memory usage statistics"""

        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()

        return {
            "rss_mb": memory_info.rss / (1024 * 1024),
            "vms_mb": memory_info.vms / (1024 * 1024),
            "percent": process.memory_percent(),
        }


class CPUProfiler:
    """CPU profiling utilities"""

    @staticmethod
    @contextmanager
    def track_cpu():
        """Track CPU usage in a context"""

        # Start tracking
        psutil.cpu_percent(interval=None)
        start_time = time.perf_counter()

        cpu_stats = {"start_time": start_time}

        try:
            yield cpu_stats
        finally:
            end_time = time.perf_counter()
            cpu_percent = psutil.cpu_percent(interval=None)

            cpu_stats["end_time"] = end_time
            cpu_stats["duration"] = end_time - start_time
            cpu_stats["cpu_percent"] = cpu_percent

    @staticmethod
    def get_cpu_usage() -> Dict[str, Any]:
        """Get current CPU usage statistics"""

        return {
            "percent": psutil.cpu_percent(interval=1),
            "per_cpu": psutil.cpu_percent(interval=1, percpu=True),
            "count": psutil.cpu_count(),
        }


class PerformanceMonitor:
    """Continuous performance monitoring"""

    def __init__(self, interval: float = 1.0):
        self.interval = interval
        self.metrics: List[Dict[str, Any]] = []

    @contextmanager
    def monitor(self):
        """Monitor performance during execution"""

        import threading

        stop_event = threading.Event()

        def collect_metrics():
            while not stop_event.is_set():
                metric = {
                    "timestamp": time.time(),
                    "memory": MemoryProfiler.get_memory_usage(),
                    "cpu": CPUProfiler.get_cpu_usage(),
                }
                self.metrics.append(metric)
                time.sleep(self.interval)

        thread = threading.Thread(target=collect_metrics)
        thread.start()

        try:
            yield self.metrics
        finally:
            stop_event.set()
            thread.join()

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of collected metrics"""

        if not self.metrics:
            return {}

        memory_values = [m["memory"]["rss_mb"] for m in self.metrics]
        cpu_values = [m["cpu"]["percent"] for m in self.metrics]

        return {
            "duration": len(self.metrics) * self.interval,
            "samples": len(self.metrics),
            "memory": {
                "avg_mb": statistics.mean(memory_values),
                "max_mb": max(memory_values),
                "min_mb": min(memory_values),
            },
            "cpu": {
                "avg_percent": statistics.mean(cpu_values),
                "max_percent": max(cpu_values),
                "min_percent": min(cpu_values),
            },
        }


# Utility functions
def benchmark_decorator(
    iterations: int = 1, warmup: int = 0, print_result: bool = True
):
    """Decorator for benchmarking functions"""

    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            benchmark = PerformanceBenchmark(suite_name=f"Benchmark: {func.__name__}")

            result = benchmark.benchmark(
                func=lambda: func(*args, **kwargs),
                name=func.__name__,
                iterations=iterations,
                warmup=warmup,
            )

            if print_result:
                print(
                    f"{func.__name__}: "
                    f"{result.duration_seconds:.3f}s "
                    f"({result.memory_mb:.2f}MB)"
                )

            return result

        return wrapper

    return decorator


def compare_implementations(
    implementations: Dict[str, Callable],
    iterations: int = 10,
    warmup: int = 2,
) -> None:
    """Compare multiple implementations of the same function"""

    benchmark = PerformanceBenchmark(suite_name="Implementation Comparison")
    benchmark.compare(implementations, iterations=iterations, warmup=warmup)
    benchmark.print_summary()
    benchmark.save_results()
