"""WhatsApp webhook router for FastAPI applications."""

from collections.abc import Callable
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel


class WhatsAppConfig(BaseModel):
    """Configuration for WhatsApp webhook."""

    verify_token: str
    webhook_secret: str | None = None
    prefix: str = "/webhook"


class WhatsAppMessage(BaseModel):
    """Base model for WhatsApp webhook messages."""

    object: str
    entry: list[dict[str, Any]]


class WhatsApp(APIRouter):
    """WhatsApp webhook router that inherits from FastAPI APIRouter."""

    def __init__(
        self,
        verify_token: str,
        webhook_secret: str | None = None,
        prefix: str = "/webhook",
        **router_kwargs: Any,  # noqa: ANN401
    ) -> None:
        """
        Initialize WhatsApp webhook router.

        Args:
            verify_token: Token for webhook verification
            webhook_secret: Optional secret for webhook signature verification
            prefix: URL prefix for webhook endpoints
            **router_kwargs: Additional arguments passed to APIRouter
        """
        super().__init__(prefix=prefix, **router_kwargs)

        self.config = WhatsAppConfig(
            verify_token=verify_token,
            webhook_secret=webhook_secret,
            prefix=prefix,
        )

        # Event handlers storage
        self._message_handlers: list[Callable[[dict[str, Any]], None]] = []
        self._status_handlers: list[Callable[[dict[str, Any]], None]] = []

        # Setup default routes
        self._setup_routes()

    def _setup_routes(self) -> None:
        """Set up default webhook routes."""

        @self.get("/")
        async def verify_webhook(
            hub_mode: str = Query(..., alias="hub.mode"),
            hub_challenge: str = Query(..., alias="hub.challenge"),
            hub_verify_token: str = Query(..., alias="hub.verify_token"),
        ) -> str:
            """Verify webhook subscription."""
            if hub_mode == "subscribe" and hub_verify_token == self.config.verify_token:
                return hub_challenge
            raise HTTPException(status_code=403, detail="Forbidden")

        @self.post("/")
        async def handle_webhook(message: WhatsAppMessage) -> dict[str, str]:
            """Handle incoming webhook messages."""
            # NOTE: Webhook signature verification could be added if webhook_secret is provided

            # Process each entry in the webhook payload
            for entry in message.entry:
                if "changes" in entry:
                    for change in entry["changes"]:
                        field = change.get("field")
                        value = change.get("value", {})

                        if field == "messages":
                            await self._handle_messages(value)
                        elif field == "message_status":
                            await self._handle_status_updates(value)

            return {"status": "ok"}

    async def _handle_messages(self, value: dict[str, Any]) -> None:
        """Handle incoming messages."""
        messages = value.get("messages", [])
        for message in messages:
            for handler in self._message_handlers:
                try:
                    handler(message)
                except Exception:  # noqa: BLE001, S112
                    # In production, this should be logged properly
                    continue

    async def _handle_status_updates(self, value: dict[str, Any]) -> None:
        """Handle message status updates."""
        statuses = value.get("statuses", [])
        for status in statuses:
            for handler in self._status_handlers:
                try:
                    handler(status)
                except Exception:  # noqa: BLE001, S112
                    # In production, this should be logged properly
                    continue

    def on_message(self, handler: Callable[[dict[str, Any]], None]) -> Callable[[dict[str, Any]], None]:
        """
        Register a message handler.

        Args:
            handler: Function to handle incoming messages

        Returns
        -------
            The registered handler function
        """
        self._message_handlers.append(handler)
        return handler

    def on_status_update(self, handler: Callable[[dict[str, Any]], None]) -> Callable[[dict[str, Any]], None]:
        """
        Register a status update handler.

        Args:
            handler: Function to handle message status updates

        Returns
        -------
            The registered handler function
        """
        self._status_handlers.append(handler)
        return handler
