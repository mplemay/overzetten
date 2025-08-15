"""Example usage of the WhatsApp webhook router."""

from fastapi import FastAPI
from overzetten import WhatsApp

app = FastAPI(title="WhatsApp Webhook Example")

# Create WhatsApp webhook router
whatsapp = WhatsApp(
    verify_token="your_verify_token_here",
    webhook_secret="your_webhook_secret_here",  # optional
    prefix="/whatsapp"
)

# Register event handlers using decorators
@whatsapp.on_message
def handle_message(message: dict) -> None:
    """Handle incoming WhatsApp messages."""
    message_type = message.get("type")
    sender = message.get("from")
    
    if message_type == "text":
        text_body = message["text"]["body"]
        print(f"Received text from {sender}: {text_body}")
        
        # Echo the message back (in real usage, you'd send via WhatsApp API)
        if text_body.lower() == "hello":
            print(f"Would reply to {sender}: Hello! How can I help you?")
    
    elif message_type == "image":
        print(f"Received image from {sender}")
        
    elif message_type == "audio":
        print(f"Received audio from {sender}")
        
    else:
        print(f"Received {message_type} message from {sender}")

@whatsapp.on_status_update
def handle_status(status: dict) -> None:
    """Handle message status updates."""
    message_id = status["id"]
    status_type = status["status"]
    recipient = status.get("recipient_id")
    
    print(f"Message {message_id} to {recipient}: {status_type}")

# Include the router in the app
app.include_router(whatsapp)

# Add a simple health check endpoint
@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    print("Starting WhatsApp webhook server...")
    print("Webhook URL: http://localhost:8000/whatsapp/")
    print("Health check: http://localhost:8000/health")
    uvicorn.run(app, host="0.0.0.0", port=8000)