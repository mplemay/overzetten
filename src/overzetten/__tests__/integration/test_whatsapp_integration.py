"""Test WhatsApp webhook router integration with FastAPI."""

from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from overzetten import WhatsApp


@pytest.fixture
def whatsapp_router():
    """Create a WhatsApp router for testing."""
    return WhatsApp(verify_token="test_verify_token")


@pytest.fixture
def app_with_whatsapp(whatsapp_router):
    """Create a FastAPI app with WhatsApp router included."""
    app = FastAPI()
    app.include_router(whatsapp_router)
    return app


@pytest.fixture
def client(app_with_whatsapp):
    """Create a test client."""
    return TestClient(app_with_whatsapp)


class TestWhatsAppWebhookVerification:
    """Test webhook verification functionality."""

    def test_successful_verification(self, client):
        """Test successful webhook verification."""
        response = client.get(
            "/webhook/",
            params={
                "hub.mode": "subscribe",
                "hub.challenge": "test_challenge",
                "hub.verify_token": "test_verify_token",
            }
        )
        assert response.status_code == 200
        assert response.text == '"test_challenge"'

    def test_invalid_verify_token(self, client):
        """Test webhook verification with invalid token."""
        response = client.get(
            "/webhook/",
            params={
                "hub.mode": "subscribe",
                "hub.challenge": "test_challenge",
                "hub.verify_token": "invalid_token",
            }
        )
        assert response.status_code == 403

    def test_invalid_mode(self, client):
        """Test webhook verification with invalid mode."""
        response = client.get(
            "/webhook/",
            params={
                "hub.mode": "invalid_mode",
                "hub.challenge": "test_challenge",
                "hub.verify_token": "test_verify_token",
            }
        )
        assert response.status_code == 403


class TestWhatsAppWebhookHandling:
    """Test webhook message handling functionality."""

    def test_basic_webhook_message(self, client):
        """Test handling a basic webhook message."""
        webhook_payload = {
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "id": "entry_id",
                    "changes": [
                        {
                            "field": "messages",
                            "value": {
                                "messaging_product": "whatsapp",
                                "metadata": {
                                    "display_phone_number": "1234567890",
                                    "phone_number_id": "phone_id"
                                },
                                "contacts": [
                                    {
                                        "profile": {
                                            "name": "Test User"
                                        },
                                        "wa_id": "user_wa_id"
                                    }
                                ],
                                "messages": [
                                    {
                                        "from": "user_wa_id",
                                        "id": "message_id",
                                        "timestamp": "1234567890",
                                        "text": {
                                            "body": "Hello World"
                                        },
                                        "type": "text"
                                    }
                                ]
                            }
                        }
                    ]
                }
            ]
        }

        response = client.post("/webhook/", json=webhook_payload)
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_status_update_webhook(self, client):
        """Test handling message status updates."""
        webhook_payload = {
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "id": "entry_id",
                    "changes": [
                        {
                            "field": "message_status",
                            "value": {
                                "messaging_product": "whatsapp",
                                "metadata": {
                                    "display_phone_number": "1234567890",
                                    "phone_number_id": "phone_id"
                                },
                                "statuses": [
                                    {
                                        "id": "message_id",
                                        "status": "delivered",
                                        "timestamp": "1234567890",
                                        "recipient_id": "user_wa_id"
                                    }
                                ]
                            }
                        }
                    ]
                }
            ]
        }

        response = client.post("/webhook/", json=webhook_payload)
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestWhatsAppEventHandlers:
    """Test event handler functionality."""

    def test_message_handler_registration(self, whatsapp_router, app_with_whatsapp):
        """Test that message handlers can be registered and called."""
        received_messages = []

        @whatsapp_router.on_message
        def handle_message(message: dict[str, Any]) -> None:
            received_messages.append(message)

        client = TestClient(app_with_whatsapp)

        webhook_payload = {
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "id": "entry_id",
                    "changes": [
                        {
                            "field": "messages",
                            "value": {
                                "messages": [
                                    {
                                        "from": "user_wa_id",
                                        "id": "message_id",
                                        "text": {"body": "Test message"},
                                        "type": "text"
                                    }
                                ]
                            }
                        }
                    ]
                }
            ]
        }

        response = client.post("/webhook/", json=webhook_payload)
        assert response.status_code == 200
        assert len(received_messages) == 1
        assert received_messages[0]["text"]["body"] == "Test message"

    def test_status_handler_registration(self, whatsapp_router, app_with_whatsapp):
        """Test that status handlers can be registered and called."""
        received_statuses = []

        @whatsapp_router.on_status_update
        def handle_status(status: dict[str, Any]) -> None:
            received_statuses.append(status)

        client = TestClient(app_with_whatsapp)

        webhook_payload = {
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "id": "entry_id",
                    "changes": [
                        {
                            "field": "message_status",
                            "value": {
                                "statuses": [
                                    {
                                        "id": "message_id",
                                        "status": "delivered",
                                        "recipient_id": "user_wa_id"
                                    }
                                ]
                            }
                        }
                    ]
                }
            ]
        }

        response = client.post("/webhook/", json=webhook_payload)
        assert response.status_code == 200
        assert len(received_statuses) == 1
        assert received_statuses[0]["status"] == "delivered"

    def test_multiple_handlers(self, whatsapp_router, app_with_whatsapp):
        """Test that multiple handlers can be registered."""
        handler1_calls = []
        handler2_calls = []

        @whatsapp_router.on_message
        def handler1(message: dict[str, Any]) -> None:
            handler1_calls.append(message)

        @whatsapp_router.on_message
        def handler2(message: dict[str, Any]) -> None:
            handler2_calls.append(message)

        client = TestClient(app_with_whatsapp)

        webhook_payload = {
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "id": "entry_id",
                    "changes": [
                        {
                            "field": "messages",
                            "value": {
                                "messages": [
                                    {
                                        "from": "user_wa_id",
                                        "id": "message_id",
                                        "text": {"body": "Test message"},
                                        "type": "text"
                                    }
                                ]
                            }
                        }
                    ]
                }
            ]
        }

        response = client.post("/webhook/", json=webhook_payload)
        assert response.status_code == 200
        assert len(handler1_calls) == 1
        assert len(handler2_calls) == 1


class TestWhatsAppConfiguration:
    """Test WhatsApp router configuration."""

    def test_custom_prefix(self):
        """Test router with custom prefix."""
        router = WhatsApp(verify_token="test", prefix="/custom")
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)

        response = client.get(
            "/custom/",
            params={
                "hub.mode": "subscribe",
                "hub.challenge": "test_challenge",
                "hub.verify_token": "test",
            }
        )
        assert response.status_code == 200

    def test_router_kwargs(self):
        """Test passing additional router kwargs."""
        router = WhatsApp(
            verify_token="test",
            tags=["whatsapp"],
            dependencies=[]
        )
        assert "whatsapp" in router.tags

    def test_config_properties(self):
        """Test that config is properly set."""
        router = WhatsApp(
            verify_token="test_token",
            webhook_secret="test_secret",
            prefix="/custom"
        )

        assert router.config.verify_token == "test_token"
        assert router.config.webhook_secret == "test_secret"
        assert router.config.prefix == "/custom"


class TestWhatsAppErrorHandling:
    """Test error handling in WhatsApp router."""

    def test_handler_exception_handling(self, whatsapp_router, app_with_whatsapp):
        """Test that exceptions in handlers don't break the webhook."""
        @whatsapp_router.on_message
        def failing_handler(message: dict[str, Any]) -> None:
            raise Exception("Handler error")

        received_messages = []

        @whatsapp_router.on_message
        def working_handler(message: dict[str, Any]) -> None:
            received_messages.append(message)

        client = TestClient(app_with_whatsapp)

        webhook_payload = {
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "id": "entry_id",
                    "changes": [
                        {
                            "field": "messages",
                            "value": {
                                "messages": [
                                    {
                                        "from": "user_wa_id",
                                        "id": "message_id",
                                        "text": {"body": "Test message"},
                                        "type": "text"
                                    }
                                ]
                            }
                        }
                    ]
                }
            ]
        }

        response = client.post("/webhook/", json=webhook_payload)
        assert response.status_code == 200
        # The working handler should still be called despite the failing handler
        assert len(received_messages) == 1
