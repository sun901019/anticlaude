"""
Video Frame Adapter — 影片關鍵幀提取適配器 (M2: ffmpeg)
=========================================================
Canonical spec: projects/anticlaude/spec_video_ingestion.md

Activation conditions — all now met (2026-03-21):
  1. ffmpeg available locally ✅ (installed 2026-03-21)
  2. Flow Lab Phase 1 (screenshot workflow) stable ✅
  3. VideoInsightArtifact in DB schema ✅ (done 2026-03-20)
  4. Approval gate risk definitions for video type ✅ (done 2026-03-20)
"""
from __future__ import annotations

import asyncio
import json
import os
import shutil
import tempfile
from pathlib import Path

from src.adapters.base import AdapterBase, AdapterResult
from src.utils.logger import get_logger

log = get_logger("adapters.video_frame_extractor")

_FFMPEG = shutil.which("ffmpeg") or "ffmpeg"
_FFPROBE = shutil.which("ffprobe") or "ffprobe"


async def _run(cmd: list[str], timeout: float = 60.0) -> tuple[int, str, str]:
    """Run a subprocess command asynchronously, return (returncode, stdout, stderr)."""
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        proc.kill()
        await proc.communicate()
        return -1, "", f"subprocess timed out after {timeout}s"
    return proc.returncode, stdout.decode("utf-8", errors="replace"), stderr.decode("utf-8", errors="replace")


async def _get_duration(video_path: str) -> float | None:
    """Use ffprobe to get video duration in seconds. Returns None on failure."""
    cmd = [
        _FFPROBE, "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        video_path,
    ]
    rc, stdout, stderr = await _run(cmd, timeout=15.0)
    if rc != 0:
        log.warning(f"ffprobe failed (rc={rc}): {stderr[:200]}")
        return None
    try:
        info = json.loads(stdout)
        return float(info["format"]["duration"])
    except (KeyError, ValueError, json.JSONDecodeError) as e:
        log.warning(f"ffprobe output parse error: {e}")
        return None


class VideoFrameAdapter(AdapterBase):
    """
    Extract keyframes from a local video file using ffmpeg.

    Payload:
        video_path (str):       absolute path to the video file
        max_frames (int):       maximum number of frames to extract (default 8)
        interval_secs (float):  extract one frame every N seconds;
                                if omitted, evenly distribute max_frames over duration
        output_dir (str):       directory to write frames; defaults to a temp dir

    Returns (AdapterResult.data):
        {
            "keyframe_paths": list[str],   # absolute paths to extracted JPEG frames
            "duration_secs": float | None, # total video duration
            "frame_count": int,
            "output_dir": str,
        }
    """
    name = "video_frame_extractor"
    risk_level = "low"
    timeout_seconds = 120
    requires_approval = False
    allowed_agents = ["ori", "craft"]

    async def execute(self, payload: dict) -> AdapterResult:
        video_path = payload.get("video_path", "")
        if not video_path:
            return AdapterResult(ok=False, error="video_path is required")

        if not os.path.isfile(video_path):
            return AdapterResult(ok=False, error=f"File not found: {video_path}")

        # Check ffmpeg available
        if not shutil.which("ffmpeg"):
            return AdapterResult(ok=False, error="ffmpeg not found on PATH — install ffmpeg first")

        max_frames: int = int(payload.get("max_frames", 8))
        max_frames = max(1, min(max_frames, 30))  # clamp 1..30
        interval_secs: float | None = payload.get("interval_secs")
        output_dir: str | None = payload.get("output_dir")

        # Get duration first
        duration = await _get_duration(video_path)

        # Determine frame extraction rate
        if interval_secs:
            fps_filter = f"fps=1/{interval_secs}"
        elif duration and duration > 0:
            # Evenly spread max_frames across duration
            calc_interval = max(duration / max_frames, 0.5)
            fps_filter = f"fps=1/{calc_interval:.2f}"
        else:
            # Fallback: 1 frame every 5 seconds
            fps_filter = "fps=1/5"

        # Create output directory
        _cleanup_dir = False
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        else:
            output_dir = tempfile.mkdtemp(prefix="aitos_frames_")
            _cleanup_dir = False  # caller's responsibility to clean up

        output_pattern = str(Path(output_dir) / "frame%04d.jpg")

        # Build ffmpeg command
        # -vf selects frames, -vframes limits total, -q:v 2 = high quality JPEG
        cmd = [
            _FFMPEG,
            "-y",                    # overwrite
            "-i", video_path,
            "-vf", fps_filter,
            "-vframes", str(max_frames),
            "-q:v", "2",             # JPEG quality (2=best, 31=worst)
            output_pattern,
        ]

        log.info(f"[VideoFrameAdapter] extracting frames from {video_path!r} → {output_dir}")
        rc, stdout, stderr = await _run(cmd, timeout=float(self.timeout_seconds - 5))

        if rc != 0:
            log.warning(f"[VideoFrameAdapter] ffmpeg failed (rc={rc}): {stderr[-300:]}")
            return AdapterResult(ok=False, error=f"ffmpeg error (rc={rc}): {stderr[-200:]}")

        # Collect extracted frames
        keyframe_paths = sorted(
            str(p) for p in Path(output_dir).glob("frame*.jpg")
            if p.is_file()
        )

        if not keyframe_paths:
            return AdapterResult(
                ok=False,
                error="ffmpeg ran but no frames were extracted — video may be too short or corrupt",
            )

        log.info(f"[VideoFrameAdapter] extracted {len(keyframe_paths)} frames")
        return AdapterResult(
            ok=True,
            data={
                "keyframe_paths": keyframe_paths,
                "duration_secs": duration,
                "frame_count": len(keyframe_paths),
                "output_dir": output_dir,
            },
        )
