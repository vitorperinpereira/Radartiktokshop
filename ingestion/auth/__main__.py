"""Interactive TikTok Shop OAuth bootstrap helper."""

from __future__ import annotations

import asyncio

from ingestion.auth import TikTokAuthSettings


async def _run_async() -> int:
    settings = TikTokAuthSettings.from_env()
    oauth = settings.build_oauth()

    print("Acesse: https://partner.tiktokshop.com")
    print("Configure o redirect local: http://localhost:8000/auth/tiktok/callback")
    print("Crie seu app e copie o AUTH_CODE gerado")
    auth_code = input("Cole seu AUTH_CODE aqui: ").strip() or settings.auth_code
    if not auth_code:
        raise RuntimeError(
            "AUTH_CODE ausente. Defina `TIKTOK_AUTH_CODE` ou cole o valor manualmente."
        )

    token = await oauth.get_access_token(auth_code)
    oauth.token_cache.save(token)
    print("Autenticacao concluida!")
    print(f"Token valido ate: {token.expires_at.isoformat()}")
    print(f"Refresh token valido ate: {token.refresh_expires_at.isoformat()}")
    return 0


def main() -> int:
    """Run the interactive TikTok Shop OAuth setup helper."""

    return asyncio.run(_run_async())


if __name__ == "__main__":
    raise SystemExit(main())
