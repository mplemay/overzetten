"""Test WhatsApp webhook router integration with FastAPI."""

import os
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from overzetten.whatsapp import WhatsApp, WhatsAppConfig


@pytest.fixture
def test_config():
    """Create a test configuration."""
    return WhatsAppConfig(
        whatsapp_phone_id="test_phone",
        whatsapp_token="test_token",
        whatsapp_verify_token="test_verify_token",
        whatsapp_app_id="test_app",
        whatsapp_app_secret="test_secret"
    )


@pytest.fixture
def whatsapp_router(test_config):
    """Create a WhatsApp router for testing."""
    return WhatsApp(config=test_config)


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

    def test_message_handler_registration_constructor(self, test_config):
        """Test that message handlers can be registered via constructor and called."""
        received_messages = []

        def handle_message(message: dict[str, Any]) -> None:
            received_messages.append(message)

        router = WhatsApp(config=test_config, on_message=handle_message)
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)

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

    def test_message_handler_registration_constructor(self, test_config):
        """Test that message handlers can be registered via constructor and called."""
        received_messages = []

        def handle_message(message: dict[str, Any]) -> None:
            received_messages.append(message)

        router = WhatsApp(config=test_config, on_message=handle_message)
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)

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

    def test_status_handler_registration(self, test_config):
        """Test that status handlers can be registered via constructor and called."""
        received_statuses = []

        def handle_status(status: dict[str, Any]) -> None:
            received_statuses.append(status)

        router = WhatsApp(config=test_config, on_status_update=handle_status)
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)

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

    def test_multiple_handlers(self, test_config):
        """Test that multiple handlers can be registered via constructor."""
        # For constructor-based approach, we can only register one handler of each type
        # but we can create multiple routers if needed
        handler1_calls = []

        def handler1(message: dict[str, Any]) -> None:
            handler1_calls.append(message)

        router = WhatsApp(config=test_config, on_message=handler1)
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)

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


class TestWhatsAppConfiguration:
    """Test WhatsApp router configuration."""

    def test_custom_prefix(self):
        """Test router with custom prefix."""
        config = WhatsAppConfig(
            whatsapp_phone_id="test_phone",
            whatsapp_token="test_token",
            whatsapp_verify_token="test",
            whatsapp_app_id="test_app",
            whatsapp_app_secret="test_secret"
        )
        router = WhatsApp(config=config, prefix="/custom")
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

    def test_include_router_with_path(self):
        """Test the API usage pattern from the comment."""
        received_messages = []

        def my_handler(message: dict[str, Any]) -> None:
            received_messages.append(message)

        # Test the exact usage pattern from the comment
        config = WhatsAppConfig(
            whatsapp_phone_id="test_phone",
            whatsapp_token="test_token",
            whatsapp_verify_token="test_token",
            whatsapp_app_id="test_app",
            whatsapp_app_secret="test_secret"
        )
        whatsapp = WhatsApp(
            config=config,
            on_message=my_handler,
            prefix=""  # No prefix since we're setting it at include_router level
        )

        app = FastAPI()
        app.include_router(router=whatsapp, prefix="/webhook/whatsapp")
        client = TestClient(app)

        # Test that the webhook verification works at the new path
        response = client.get(
            "/webhook/whatsapp/",
            params={
                "hub.mode": "subscribe",
                "hub.challenge": "test_challenge",
                "hub.verify_token": "test_token",
            }
        )
        assert response.status_code == 200

        # Test that messages are processed
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

        response = client.post("/webhook/whatsapp/", json=webhook_payload)
        assert response.status_code == 200
        assert len(received_messages) == 1

    def test_router_kwargs(self):
        """Test passing additional router kwargs."""
        config = WhatsAppConfig(
            whatsapp_phone_id="test_phone",
            whatsapp_token="test_token",
            whatsapp_verify_token="test",
            whatsapp_app_id="test_app",
            whatsapp_app_secret="test_secret"
        )
        router = WhatsApp(
            config=config,
            tags=["whatsapp"],
            dependencies=[]
        )
        assert "whatsapp" in router.tags

    def test_config_properties(self):
        """Test that config is properly set."""
        config = WhatsAppConfig(
            whatsapp_phone_id="test_phone",
            whatsapp_token="test_token",
            whatsapp_verify_token="test_verify_token",
            whatsapp_app_id="test_app",
            whatsapp_app_secret="test_secret"
        )
        router = WhatsApp(
            config=config,
            prefix="/custom"
        )

        assert router.config.whatsapp_phone_id == "test_phone"
        assert router.config.whatsapp_token == "test_token"
        assert router.config.whatsapp_verify_token == "test_verify_token"
        assert router.config.whatsapp_app_id == "test_app"
        assert router.config.whatsapp_app_secret == "test_secret"

    def test_config_from_environment(self):
        """Test that config can be loaded from environment variables."""
        # Set environment variables
        os.environ["WHATSAPP_PHONE_ID"] = "env_phone"
        os.environ["WHATSAPP_TOKEN"] = "env_token"
        os.environ["WHATSAPP_VERIFY_TOKEN"] = "env_verify"
        os.environ["WHATSAPP_APP_ID"] = "env_app"
        os.environ["WHATSAPP_APP_SECRET"] = "env_secret"

        try:
            # Create router without explicit config (should load from env)
            router = WhatsApp()

            assert router.config.whatsapp_phone_id == "env_phone"
            assert router.config.whatsapp_token == "env_token"
            assert router.config.whatsapp_verify_token == "env_verify"
            assert router.config.whatsapp_app_id == "env_app"
            assert router.config.whatsapp_app_secret == "env_secret"
        finally:
            # Clean up environment variables
            for key in ["WHATSAPP_PHONE_ID", "WHATSAPP_TOKEN", "WHATSAPP_VERIFY_TOKEN",
                       "WHATSAPP_APP_ID", "WHATSAPP_APP_SECRET"]:
                os.environ.pop(key, None)


class TestWhatsAppErrorHandling:
    """Test error handling in WhatsApp router."""

    def test_handler_exception_handling(self, test_config):
        """Test that exceptions in handlers don't break the webhook."""
        # With constructor-based approach, we'll test a single handler that fails
        def failing_handler(message: dict[str, Any]) -> None:
            raise Exception("Handler error")

        router = WhatsApp(config=test_config, on_message=failing_handler)
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)

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
        # Should still return 200 even if handler fails (exception is caught)
        assert response.status_code == 200
