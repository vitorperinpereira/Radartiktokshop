"""FastAPI application entrypoint."""

from __future__ import annotations

import logging
from datetime import date
from html import escape

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from apps.api.deps import get_session
from apps.api.garage_router import router as garage_router
from apps.api.media_router import router as media_router
from apps.api.ranking_api.router import router as ranking_router
from apps.api.schemas import (
    ContentAnglesResponse,
    PipelineRunHistoryResponse,
    ProductDetailResponse,
    ProductVideosResponse,
    RankingResponse,
    ReportHistoryResponse,
)
from apps.dashboard.router import router as dashboard_router
from ingestion.auth import TikTokAuthSettings
from services.reporting import (
    get_product_detail,
    list_pipeline_run_history,
    list_report_history,
    list_weekly_ranking,
)
from services.shared.config import AppSettings, get_settings
from services.shared.db.models import ContentAngle, ProductSnapshot
from services.shared.db.session import build_session_factory
from services.shared.health import build_health_payload
from services.shared.logging import configure_logging

logger = logging.getLogger(__name__)
LOCAL_FRONTEND_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:4173",
    "http://127.0.0.1:4173",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

session_dependency = Depends(get_session)


def _render_status_page(title: str, message: str, *, status_code: int) -> HTMLResponse:
    body = f"""<!doctype html>
<html lang="pt-BR">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{escape(title)}</title>
    <style>
      :root {{
        color-scheme: light;
        font-family: "Segoe UI", Arial, sans-serif;
      }}
      body {{
        margin: 0;
        min-height: 100vh;
        display: grid;
        place-items: center;
        background: linear-gradient(160deg, #f5f7fb 0%, #eef6ff 100%);
        color: #10233f;
      }}
      main {{
        width: min(100%, 40rem);
        margin: 1.5rem;
        padding: 2rem;
        border-radius: 1.25rem;
        background: #ffffff;
        box-shadow: 0 24px 80px rgba(16, 35, 63, 0.12);
      }}
      h1 {{
        margin: 0 0 0.75rem;
        font-size: 1.5rem;
      }}
      p {{
        margin: 0;
        line-height: 1.6;
      }}
      code {{
        font-family: Consolas, "Courier New", monospace;
      }}
    </style>
  </head>
  <body>
    <main>
      <h1>{escape(title)}</h1>
      <p>{escape(message)}</p>
    </main>
  </body>
</html>
"""
    return HTMLResponse(content=body, status_code=status_code)


def create_app(settings: AppSettings | None = None) -> FastAPI:
    active_settings = settings or get_settings()
    configure_logging(active_settings.log_level)

    app = FastAPI(
        title=active_settings.app_name,
        version="0.1.0",
        summary="Read and control API for Creator Product Radar.",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=LOCAL_FRONTEND_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.state.settings = active_settings
    app.state.session_factory = build_session_factory(settings=active_settings)

    @app.get("/", tags=["ops"])
    def root() -> dict[str, str]:
        return {
            "app": active_settings.app_name,
            "docs": "/docs",
            "status": "ok",
        }

    @app.get("/health", tags=["ops"])
    def health() -> dict[str, object]:
        return build_health_payload(active_settings, surface="api")

    @app.get("/auth/tiktok/callback", tags=["ops"])
    async def tiktok_auth_callback(
        code: str | None = None,
        auth_code: str | None = Query(default=None, alias="auth_code"),
        state: str | None = None,
    ) -> HTMLResponse:
        resolved_code = (auth_code or code or "").strip()
        if not resolved_code:
            return _render_status_page(
                "Codigo de autorizacao ausente",
                "A callback local precisa receber `code` ou `auth_code` na query string.",
                status_code=400,
            )

        try:
            auth_settings = TikTokAuthSettings.from_env()
        except ValueError as exc:
            logger.error("TikTok OAuth callback misconfigured: %s", exc)
            return _render_status_page(
                "Configuracao incompleta",
                str(exc),
                status_code=500,
            )

        expected_state = auth_settings.oauth_state.strip()
        resolved_state = (state or "").strip()
        if not expected_state:
            logger.error("TikTok OAuth callback missing TIKTOK_OAUTH_STATE configuration.")
            return _render_status_page(
                "Configuracao incompleta",
                "Defina `TIKTOK_OAUTH_STATE` para validar a callback OAuth local.",
                status_code=500,
            )
        if resolved_state != expected_state:
            logger.warning("TikTok OAuth callback rejected due to invalid state.")
            return _render_status_page(
                "State invalido",
                "A callback local recebeu um `state` ausente ou diferente do esperado.",
                status_code=400,
            )

        oauth = auth_settings.build_oauth()

        try:
            token = await oauth.get_access_token(resolved_code)
        except RuntimeError as exc:
            logger.exception("TikTok OAuth callback failed during token exchange.")
            return _render_status_page(
                "Falha ao trocar o codigo",
                str(exc),
                status_code=502,
            )

        oauth.token_cache.save(token)
        return _render_status_page(
            "Autenticacao concluida",
            (
                "O token do TikTok Shop foi salvo com sucesso no cache local. "
                f"Valido ate {token.expires_at.isoformat()}."
            ),
            status_code=200,
        )

    @app.get("/rankings", tags=["read"], response_model=RankingResponse)
    def rankings(
        week_start: date | None = None,
        limit: int = Query(default=50, ge=1, le=500),
        category: str | None = None,
        classification: str | None = None,
        hide_high_saturation: bool = False,
        session: Session = session_dependency,
    ) -> dict[str, object]:
        return list_weekly_ranking(
            session,
            week_start=week_start,
            limit=limit,
            category=category,
            classification=classification,
            hide_high_saturation=hide_high_saturation,
        )

    @app.get("/products/{product_id}", tags=["read"], response_model=ProductDetailResponse)
    def product_detail(
        product_id: str,
        week_start: date | None = None,
        session: Session = session_dependency,
    ) -> dict[str, object]:
        payload = get_product_detail(
            session,
            product_id=product_id,
            week_start=week_start,
        )
        if payload is None:
            raise HTTPException(
                status_code=404,
                detail=f"No persisted product score found for `{product_id}`.",
            )
        return payload

    @app.get("/history/pipeline-runs", tags=["history"], response_model=PipelineRunHistoryResponse)
    def pipeline_run_history(
        limit: int = Query(default=20, ge=1, le=200),
        session: Session = session_dependency,
    ) -> dict[str, object]:
        return list_pipeline_run_history(session, limit=limit)

    @app.get("/history/reports", tags=["history"], response_model=ReportHistoryResponse)
    def report_history(
        limit: int = Query(default=20, ge=1, le=200),
        session: Session = session_dependency,
    ) -> dict[str, object]:
        return list_report_history(session, limit=limit)

    @app.get(
        "/products/{product_id}/content-angles",
        tags=["read"],
        response_model=ContentAnglesResponse,
    )
    def product_content_angles(
        product_id: str,
        week_start: date | None = None,
        session: Session = session_dependency,
    ) -> dict[str, object]:
        query = (
            session.query(ContentAngle)
            .filter(ContentAngle.product_id == product_id)
            .order_by(ContentAngle.created_at.desc())
        )
        if week_start is not None:
            query = query.filter(ContentAngle.week_start == week_start)
        rows = query.all()
        return {
            "product_id": product_id,
            "count": len(rows),
            "angles": [
                {
                    "angle_type": r.angle_type,
                    "hook_text": r.hook_text,
                    "supporting_rationale": r.supporting_rationale,
                    "week_start": str(r.week_start),
                }
                for r in rows
            ],
        }

    @app.get(
        "/products/{product_id}/videos",
        tags=["read"],
        response_model=ProductVideosResponse,
    )
    def product_videos(
        product_id: str,
        session: Session = session_dependency,
    ) -> dict[str, object]:
        snapshots = (
            session.query(ProductSnapshot)
            .filter(ProductSnapshot.product_id == product_id)
            .order_by(ProductSnapshot.captured_at.desc())
            .limit(5)
            .all()
        )
        videos: list[dict[str, object]] = []
        source = "raw_payload"
        seen_urls: set[str] = set()
        for snap in snapshots:
            payload = snap.raw_payload or {}
            for key in (
                "videoUrl",
                "video_url",
                "videos",
                "topVideos",
                "relatedVideos",
            ):
                val = payload.get(key)
                if val is None:
                    continue
                if isinstance(val, str) and val not in seen_urls:
                    seen_urls.add(val)
                    videos.append({"video_url": val})
                elif isinstance(val, list):
                    for item in val:
                        if isinstance(item, str) and item not in seen_urls:
                            seen_urls.add(item)
                            videos.append({"video_url": item})
                        elif isinstance(item, dict):
                            url = (
                                item.get("videoUrl") or item.get("video_url") or item.get("url", "")
                            )
                            if url and url not in seen_urls:
                                seen_urls.add(url)
                                videos.append(
                                    {
                                        "video_url": url,
                                        "thumbnail_url": item.get("thumbnail")
                                        or item.get("thumbnailUrl"),
                                        "title": item.get("title") or item.get("desc"),
                                        "views": item.get("views") or item.get("playCount"),
                                    }
                                )
        return {
            "product_id": product_id,
            "videos": videos[:10],
            "source": source,
        }

    app.include_router(dashboard_router)
    app.include_router(ranking_router, prefix="/api/ranking")
    app.include_router(garage_router, prefix="/api")
    app.include_router(media_router, prefix="/api/media", tags=["media"])
    return app


app = create_app()
