"""
Performance Testing Module

Provides benchmarking and performance testing utilities for the autonomous
development system.
"""

from .benchmark import (
    PerformanceBenchmark,
    BenchmarkResult,
    BenchmarkSuite,
    MemoryProfiler,
    CPUProfiler,
    PerformanceMonitor,
    benchmark_decorator,
    compare_implementations,
)

__all__ = [
    "PerformanceBenchmark",
    "BenchmarkResult",
    "BenchmarkSuite",
    "MemoryProfiler",
    "CPUProfiler",
    "PerformanceMonitor",
    "benchmark_decorator",
    "compare_implementations",
]

__version__ = "0.1.0"
