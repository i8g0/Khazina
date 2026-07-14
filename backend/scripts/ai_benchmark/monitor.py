"""Resource sampling utilities for AI pipeline benchmarks."""

from __future__ import annotations

import platform
import subprocess
import sys
from dataclasses import dataclass, field
from typing import Any

try:
    import psutil
except ImportError:  # pragma: no cover - optional at runtime
    psutil = None  # type: ignore[assignment]


@dataclass(frozen=True, slots=True)
class HardwareSummary:
    platform: str
    processor: str
    cpu_count: int
    total_ram_gb: float | None
    gpu_name: str | None
    gpu_vram_total_mb: float | None
    gpu_available: bool


@dataclass
class ResourceSample:
    timestamp: float
    process_rss_mb: float | None
    system_ram_used_mb: float | None
    system_ram_percent: float | None
    cpu_percent: float | None
    gpu_utilization_percent: float | None
    gpu_vram_used_mb: float | None


@dataclass
class ResourceSummary:
    samples: list[ResourceSample] = field(default_factory=list)
    peak_process_rss_mb: float | None = None
    peak_system_ram_used_mb: float | None = None
    peak_cpu_percent: float | None = None
    peak_gpu_utilization_percent: float | None = None
    peak_gpu_vram_used_mb: float | None = None

    def absorb(self, sample: ResourceSample) -> None:
        self.samples.append(sample)
        self.peak_process_rss_mb = _max(self.peak_process_rss_mb, sample.process_rss_mb)
        self.peak_system_ram_used_mb = _max(
            self.peak_system_ram_used_mb, sample.system_ram_used_mb
        )
        self.peak_cpu_percent = _max(self.peak_cpu_percent, sample.cpu_percent)
        self.peak_gpu_utilization_percent = _max(
            self.peak_gpu_utilization_percent, sample.gpu_utilization_percent
        )
        self.peak_gpu_vram_used_mb = _max(
            self.peak_gpu_vram_used_mb, sample.gpu_vram_used_mb
        )


def _max(current: float | None, value: float | None) -> float | None:
    if value is None:
        return current
    if current is None:
        return value
    return max(current, value)


def collect_hardware_summary() -> HardwareSummary:
    total_ram_gb: float | None = None
    if psutil is not None:
        total_ram_gb = round(psutil.virtual_memory().total / (1024**3), 2)

    gpu_name, vram_total, gpu_available = _query_nvidia_gpu()
    return HardwareSummary(
        platform=platform.platform(),
        processor=platform.processor() or platform.machine(),
        cpu_count=(psutil.cpu_count(logical=True) if psutil else None) or 0,
        total_ram_gb=total_ram_gb,
        gpu_name=gpu_name,
        gpu_vram_total_mb=vram_total,
        gpu_available=gpu_available,
    )


def _query_nvidia_gpu() -> tuple[str | None, float | None, bool]:
    try:
        result = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=name,memory.total",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None, None, False
    if result.returncode != 0 or not result.stdout.strip():
        return None, None, False
    line = result.stdout.strip().splitlines()[0]
    parts = [part.strip() for part in line.split(",")]
    if len(parts) < 2:
        return parts[0] if parts else None, None, True
    try:
        vram = float(parts[1])
    except ValueError:
        vram = None
    return parts[0], vram, True


def sample_resources(process: Any | None = None) -> ResourceSample:
    import time

    process_rss_mb: float | None = None
    system_ram_used_mb: float | None = None
    system_ram_percent: float | None = None
    cpu_percent: float | None = None

    if psutil is not None:
        vm = psutil.virtual_memory()
        system_ram_used_mb = round(vm.used / (1024**2), 2)
        system_ram_percent = float(vm.percent)
        cpu_percent = float(psutil.cpu_percent(interval=0.1))
        target = process or psutil.Process()
        process_rss_mb = round(target.memory_info().rss / (1024**2), 2)

    gpu_util, gpu_vram = _sample_gpu()
    return ResourceSample(
        timestamp=time.time(),
        process_rss_mb=process_rss_mb,
        system_ram_used_mb=system_ram_used_mb,
        system_ram_percent=system_ram_percent,
        cpu_percent=cpu_percent,
        gpu_utilization_percent=gpu_util,
        gpu_vram_used_mb=gpu_vram,
    )


def _sample_gpu() -> tuple[float | None, float | None]:
    try:
        result = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=utilization.gpu,memory.used",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None, None
    if result.returncode != 0 or not result.stdout.strip():
        return None, None
    parts = [part.strip() for part in result.stdout.strip().splitlines()[0].split(",")]
    if len(parts) < 2:
        return None, None
    try:
        return float(parts[0]), float(parts[1])
    except ValueError:
        return None, None


def require_psutil() -> None:
    if psutil is None:
        print("psutil is required for AI benchmarks: pip install psutil", file=sys.stderr)
        raise SystemExit(1)
