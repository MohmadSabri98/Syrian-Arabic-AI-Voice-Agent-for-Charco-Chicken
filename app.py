from fastapi import FastAPI, File, UploadFile, Body
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
app = FastAPI()

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

@app.get("/", response_class=JSONResponse)
async def health_check():
    return {"message": "Syrian Voice Assistant is running!"}


@app.post("/voice-agent", response_class=JSONResponse)
async def handle_audio_request(file: UploadFile = File(...)):
    try:
        audio_bytes = await file.read()
        response = await voice_agent_service.handle_audio_request(audio_bytes)
        return response
    except Exception as e:
        print(f"[ERROR] {e}")
        return JSONResponse({"error": "Internal server error."}, status_code=500)


@app.post("/submit-order", response_class=JSONResponse)
async def submit_order(request: Request):
    data = await request.json()
    name = data.get("name")
    order = data.get("order")
    dialog_history = data.get("dialog_history", [])
    response_dict, status_code = order_service.process_order_api_request(name, order, dialog_history)
    return JSONResponse(response_dict, status_code=status_code)


@app.get("/list-orders", response_class=JSONResponse)
async def list_orders():
    """Get all orders from JSON file"""
    try:
        orders = order_service.list_orders()
        return JSONResponse({
            "orders": orders,
            "total_count": len(orders)
        })
    except Exception as e:
        print(f"[ERROR] {e}")
        return JSONResponse({"error": "Failed to retrieve orders."}, status_code=500)


@app.get("/order/{order_id}", response_class=JSONResponse)
async def get_order_by_id(order_id: str):
    """Get a specific order by ID"""
    try:
        order = order_service.get_order_by_id(order_id)
        if order:
            return JSONResponse(order)
        else:
            return JSONResponse({"error": "Order not found."}, status_code=404)
    except Exception as e:
        print(f"[ERROR] {e}")
        return JSONResponse({"error": "Failed to retrieve order."}, status_code=500)


@app.post("/detect-intent", response_class=JSONResponse)
async def detect_intent_endpoint(text: str = Body(..., embed=True)):
    result = intent_service.process_intent_request(text, voice_agent_service)
    return JSONResponse(result)

@app.post("/tts", response_class=JSONResponse)
async def tts_endpoint(text: str = Body(..., embed=True)):
    audio_base64 = voice_agent_service.generate_audio(text)
    return JSONResponse({"audio_base64": audio_base64})

# ========== Run ==========

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
