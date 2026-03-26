"""
AITOS Workflow Runtime
======================
Five core primitives:
  run        - a top-level workflow execution instance
  task       - a single agent step inside a run
  event      - an immutable log entry for anything that happened
  artifact   - a file or DB record produced by a task
  approval   - a human-approval gate that can pause and resume a run

Usage:
    from src.workflows.runner import create_run, start_task, complete_task
    from src.workflows.approval import request_approval, decide_approval
    from src.workflows.artifacts import save_artifact
"""
