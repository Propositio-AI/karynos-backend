from posthog import identify_context, new_context

from settings import settings


class PostHogMiddleware:
    """Pure ASGI middleware that wraps each request in a PostHog context.

    Extracts the dreamer ID from the X-Dreamer-Id header and identifies
    the user in the context so route handlers can call capture() directly.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or settings.POSTHOG_DISABLED:
            await self.app(scope, receive, send)
            return

        dreamer_id = self._get_dreamer_id(scope)

        with new_context():
            if dreamer_id:
                identify_context(dreamer_id)

            await self.app(scope, receive, send)

    def _get_dreamer_id(self, scope) -> str | None:
        headers = dict(scope.get("headers", []))
        raw = headers.get(b"x-dreamer-id", b"").decode("utf-8")
        return raw if raw else None
