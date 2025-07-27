import base64
import requests
from services.impl.order_service_impl import OrderServiceImpl
from services.impl.intent_handlers.factory import IntentHandlerFactory

class VoiceAgentServiceImpl:
    def __init__(self, tts_service, whisper_service, intent_service):
        self.tts_service = tts_service
        self.whisper_service = whisper_service
        self.intent_service = intent_service
        self.order_service = OrderServiceImpl()
    
    async def handle_audio_request(self, audio_bytes: bytes) -> dict:
        """Handle audio request: transcribe, detect intent, generate response"""
        try:
            # Transcribe audio
            transcription = await self.whisper_service.transcribe_audio(audio_bytes)
            
            # Extract intent and generate response
            intent_info = self.extract_intent(transcription)
            
            # Generate audio for the response
            reply_text = intent_info.get("reply_text", "")
            audio_base64 = self.generate_audio(reply_text)
            
            return {
                "transcription": transcription,
                "intent": intent_info,
                "reply_text": reply_text,
                "audio_base64": audio_base64
            }
        except Exception as e:
            print(f"Error handling audio request: {e}")
            return {
                "transcription": "",
                "intent": {"error": str(e)},
                "reply_text": "عذراً، حدث خطأ في معالجة الطلب.",
                "audio_base64": ""
            }
    
    def extract_intent(self, transcription: str) -> dict:
        """Extract intent from transcription using appropriate handler"""
        try:
            order_is_valid = False  # Always initialize
            intent_info = self.intent_service.detect_intent(transcription)
            # Ensure intent_info is a dict
            if isinstance(intent_info, str):
                import json
                try:
                    intent_info = json.loads(intent_info)
                except Exception:
                    intent_info = {}
            intent_type = intent_info.get("intent", "")
            handler = IntentHandlerFactory.get_handler(intent_type)
            return handler.handle(transcription, intent_info, self)
        except Exception as e:
            print(f"Error extracting intent: {e}")
            return {
                "intent": "unknown",
                "reply_text": "عذراً، لم أفهم ما تقصده.",
                "order_is_valid": False
            }
    
    def generate_audio(self, text: str) -> str:
        """Generate audio from text using ElevenLabs"""
        try:
            if not text or text.strip() == "":
                print("Warning: Empty text provided for audio generation")
                return ""
            
            print(f"Generating audio for text: {text[:50]}...")
            audio_bytes = self.tts_service.synthesize_speech(text)
            
            if not audio_bytes:
                print("Warning: TTS service returned empty audio bytes")
                return ""
            
            print(f"Generated audio bytes: {len(audio_bytes)} bytes")
            audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
            print(f"Encoded audio base64 length: {len(audio_base64)}")
            
            return audio_base64
        except Exception as e:
            print(f"Error generating audio: {e}")
            import traceback
            traceback.print_exc()
            return "" 