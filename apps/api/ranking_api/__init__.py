"""Ranking API router and service for the FastAPI app."""

from apps.api.ranking_api.router import ranking_service, router

router.ranking_service = ranking_service

__all__ = ["ranking_service", "router"]
