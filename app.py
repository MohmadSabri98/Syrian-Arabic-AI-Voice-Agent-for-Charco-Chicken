from fastapi import FastAPI, File, UploadFile, Body, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
import re

from services.impl.tts_service_impl import TTSServiceImpl
from services.impl.whisper_service_impl import WhisperServiceImpl
from services.impl.intent_service_impl import IntentServiceImpl
from services.impl.voice_agent_service_impl import VoiceAgentServiceImpl
from services.impl.order_service_impl import OrderServiceImpl
from constants.app_constants import DEFAULT_REPLY
from fastapi import Request
import uuid

try:
    load_dotenv()
except Exception as e:
    print(f"Warning: Could not load .env file: {e}")

PORT = int(os.getenv('PORT', 5050))

# ========== App Setup ==========
app = FastAPI(
    title="Syrian Arabic AI Voice Agent API",
    description="A simple API for Charco Chicken's Arabic voice assistant. Provides endpoints for voice, order, and intent processing.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== Dependency Injection ==========
tts_service = TTSServiceImpl()
whisper_service = WhisperServiceImpl()
intent_service = IntentServiceImpl()
voice_agent_service = VoiceAgentServiceImpl(tts_service, whisper_service, intent_service)
order_service = OrderServiceImpl()

orders_db = []



# ========== Routes ==========

@app.get(
    "/",
    summary="Health check",
    description="Check if the API is running.",
    response_description="A status message."
)
async def health_check():
    return {"message": "Syrian Voice Assistant is running!"}

@app.post(
    "/voice-agent",
    summary="Process Arabic audio",
    description="Takes an audio file in Arabic and returns a transcription, intent, and audio reply.",
    response_description="A JSON object with transcription, intent, reply_text, and audio_base64."
)
async def handle_audio_request(file: UploadFile = File(...)):
    try:
        audio_bytes = await file.read()
        response = await voice_agent_service.handle_audio_request(audio_bytes)
        return response
    except Exception as e:
        print(f"[ERROR] {e}")
        raise HTTPException(status_code=500, detail="Internal server error.")

@app.post(
    "/submit-order",
    summary="Submit a customer order",
    description="Submit an order with name, items, and optional dialog history.",
    response_description="Order confirmation with order_id and eta."
)
async def submit_order(
    request: Request,
    swagger_body: dict = Body(
        example={
            "name": "أحمد",
            "order": ["دجاج مشوي", "بطاطا مقلية"],
            "dialog_history": ["مرحبا", "أريد طلب دجاج مشوي"]
        },
        description="Example order body for Swagger UI. Ignored by backend logic."
    )
):
    data = await request.json()
    name = data.get("name")
    order = data.get("order")
    dialog_history = data.get("dialog_history", [])
    response_dict, status_code = order_service.process_order_api_request(name, order, dialog_history)
    return JSONResponse(response_dict, status_code=status_code)

@app.get(
    "/list-orders",
    summary="List all orders",
    description="Retrieve all orders from the database.",
    response_description="A list of all orders."
)
async def list_orders():
    try:
        orders = order_service.list_orders()
        return JSONResponse({
            "orders": orders,
            "total_count": len(orders)
        })
    except Exception as e:
        print(f"[ERROR] {e}")
        return JSONResponse({"error": "Failed to retrieve orders."}, status_code=500)

@app.get(
    "/order/{order_id}",
    summary="Get order by ID",
    description="Retrieve a specific order by its Arabic order ID.",
    response_description="Order details or error if not found."
)
async def get_order_by_id(order_id: str):
    try:
        order = order_service.get_order_by_id(order_id)
        if order:
            return JSONResponse(order)
        else:
            return JSONResponse({"error": "Order not found."}, status_code=404)
    except Exception as e:
        print(f"[ERROR] {e}")
        return JSONResponse({"error": "Failed to retrieve order."}, status_code=500)

@app.post(
    "/detect-intent",
    summary="Detect intent from text",
    description="Detect user intent from Arabic text input.",
    response_description="Detected intent and generated reply."
)
async def detect_intent_endpoint(text: str = Body(..., embed=True)):
    result = intent_service.process_intent_request(text, voice_agent_service)
    return JSONResponse(result)

@app.post(
    "/tts",
    summary="Text-to-speech",
    description="Convert Arabic text to speech using ElevenLabs.",
    response_description="Base64 encoded audio."
)
async def tts_endpoint(text: str = Body(..., embed=True)):
    audio_base64 = voice_agent_service.generate_audio(text)
    return JSONResponse({"audio_base64": audio_base64})

# ========== Run ==========

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
