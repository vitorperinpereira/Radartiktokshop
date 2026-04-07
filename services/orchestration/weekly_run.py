"""Compatibility wrapper for the renamed pipeline-run module."""

from services.orchestration.run_pipeline import execute_pipeline_run

execute_weekly_run = execute_pipeline_run
