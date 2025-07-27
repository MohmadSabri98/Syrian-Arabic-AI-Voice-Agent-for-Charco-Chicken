import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from services.impl.voice_agent_service_impl import VoiceAgentServiceImpl
from unittest.mock import MagicMock, AsyncMock, patch
import base64

@pytest.fixture
def voice_agent_service():
    tts = MagicMock()
    whisper = MagicMock()
    intent = MagicMock()
    service = VoiceAgentServiceImpl(tts, whisper, intent)
    return service

@pytest.fixture
def mock_services():
    """Create mock services for testing"""
    tts = MagicMock()
    whisper = MagicMock()
    intent = MagicMock()
    return tts, whisper, intent

def test_extract_intent_should_return_dict(voice_agent_service):
    # Arrange
    voice_agent_service.intent_service.detect_intent.return_value = '{"intent": "question", "name": null, "response": "جواب"}'
    # Act
    result = voice_agent_service.extract_intent("ما هو الوقت المتوقع؟")
    # Assert
    assert isinstance(result, dict)
    assert result["intent"] == "question"
    # Check for actual response content
    assert "reply_text" in result

def test_extract_intent_should_handle_string_response(voice_agent_service):
    # Arrange
    voice_agent_service.intent_service.detect_intent.return_value = '{"intent": "place_order", "items": ["بيتزا"]}'
    # Act
    result = voice_agent_service.extract_intent("أريد بيتزا")
    # Assert
    assert isinstance(result, dict)
    assert "intent" in result

def test_extract_intent_should_handle_dict_response(voice_agent_service):
    # Arrange
    voice_agent_service.intent_service.detect_intent.return_value = {"intent": "greeting", "reply_text": "مرحبا"}
    # Act
    result = voice_agent_service.extract_intent("مرحبا")
    # Assert
    assert isinstance(result, dict)
    assert result["intent"] == "greeting"

def test_extract_intent_should_handle_exception(voice_agent_service):
    # Arrange
    voice_agent_service.intent_service.detect_intent.side_effect = Exception("Intent detection failed")
    # Act
    result = voice_agent_service.extract_intent("test")
    # Assert
    assert result["intent"] == "unknown"
    assert "عذراً، لم أفهم ما تقصده" in result["reply_text"]

def test_generate_audio_should_return_base64_string(voice_agent_service):
    # Arrange
    voice_agent_service.tts_service.synthesize_speech.return_value = b"audio-bytes"
    # Act
    audio_b64 = voice_agent_service.generate_audio("test")
    # Assert
    assert isinstance(audio_b64, str)
    assert len(audio_b64) > 0

def test_generate_audio_should_return_empty_string_for_empty_text(voice_agent_service):
    # Arrange
    # Act
    audio_b64 = voice_agent_service.generate_audio("")
    # Assert
    assert audio_b64 == ""

def test_generate_audio_should_return_empty_string_for_whitespace_text(voice_agent_service):
    # Arrange
    # Act
    audio_b64 = voice_agent_service.generate_audio("   ")
    # Assert
    assert audio_b64 == ""

def test_generate_audio_should_handle_tts_exception(voice_agent_service):
    # Arrange
    voice_agent_service.tts_service.synthesize_speech.side_effect = Exception("TTS failed")
    # Act
    audio_b64 = voice_agent_service.generate_audio("test")
    # Assert
    assert audio_b64 == ""

def test_generate_audio_should_handle_empty_audio_bytes(voice_agent_service):
    # Arrange
    voice_agent_service.tts_service.synthesize_speech.return_value = b""
    # Act
    audio_b64 = voice_agent_service.generate_audio("test")
    # Assert
    assert audio_b64 == ""

def test_generate_audio_should_encode_audio_correctly(voice_agent_service):
    # Arrange
    test_audio = b"test audio bytes"
    voice_agent_service.tts_service.synthesize_speech.return_value = test_audio
    # Act
    audio_b64 = voice_agent_service.generate_audio("test")
    # Assert
    expected_b64 = base64.b64encode(test_audio).decode("utf-8")
    assert audio_b64 == expected_b64

@pytest.mark.asyncio
async def test_handle_audio_request_should_return_complete_response(mock_services):
    # Arrange
    tts, whisper, intent = mock_services
    whisper.transcribe_audio = AsyncMock(return_value="مرحبا")
    intent.detect_intent.return_value = '{"intent": "greeting", "reply_text": "مرحبا بك"}'
    tts.synthesize_speech.return_value = b"audio-bytes"
    
    service = VoiceAgentServiceImpl(tts, whisper, intent)
    audio_bytes = b"test audio"
    
    # Act
    result = await service.handle_audio_request(audio_bytes)
    
    # Assert
    assert result["transcription"] == "مرحبا"
    assert result["reply_text"] == "مرحبا بك"
    assert "audio_base64" in result
    assert "intent" in result

@pytest.mark.asyncio
async def test_handle_audio_request_should_handle_whisper_exception(mock_services):
    # Arrange
    tts, whisper, intent = mock_services
    whisper.transcribe_audio = AsyncMock(side_effect=Exception("Whisper failed"))
    
    service = VoiceAgentServiceImpl(tts, whisper, intent)
    audio_bytes = b"test audio"
    
    # Act
    result = await service.handle_audio_request(audio_bytes)
    
    # Assert
    assert result["transcription"] == ""
    assert "عذراً، حدث خطأ في معالجة الطلب" in result["reply_text"]
    assert "error" in result["intent"]

@pytest.mark.asyncio
async def test_handle_audio_request_should_handle_intent_exception(mock_services):
    # Arrange
    tts, whisper, intent = mock_services
    whisper.transcribe_audio = AsyncMock(return_value="مرحبا")
    intent.detect_intent.side_effect = Exception("Intent detection failed")
    
    service = VoiceAgentServiceImpl(tts, whisper, intent)
    audio_bytes = b"test audio"
    
    # Act
    result = await service.handle_audio_request(audio_bytes)
    
    # Assert
    assert result["transcription"] == "مرحبا"
    assert "عذراً، لم أفهم ما تقصده" in result["reply_text"]

@pytest.mark.asyncio
async def test_handle_audio_request_should_handle_tts_exception(mock_services):
    # Arrange
    tts, whisper, intent = mock_services
    whisper.transcribe_audio = AsyncMock(return_value="مرحبا")
    intent.detect_intent.return_value = '{"intent": "greeting", "reply_text": "مرحبا بك"}'
    tts.synthesize_speech.side_effect = Exception("TTS failed")
    
    service = VoiceAgentServiceImpl(tts, whisper, intent)
    audio_bytes = b"test audio"
    
    # Act
    result = await service.handle_audio_request(audio_bytes)
    
    # Assert
    assert result["transcription"] == "مرحبا"
    assert result["reply_text"] == "مرحبا بك"
    assert result["audio_base64"] == ""

def test_voice_agent_service_should_have_order_service(voice_agent_service):
    # Assert
    assert hasattr(voice_agent_service, 'order_service')
    assert voice_agent_service.order_service is not None

def test_extract_intent_should_use_intent_handler_factory(voice_agent_service):
    # Arrange
    voice_agent_service.intent_service.detect_intent.return_value = '{"intent": "place_order", "items": ["بيتزا"]}'
    
    with patch('services.impl.voice_agent_service_impl.IntentHandlerFactory') as mock_factory:
        mock_handler = MagicMock()
        mock_handler.handle.return_value = {"intent": "place_order", "reply_text": "تم الطلب"}
        mock_factory.get_handler.return_value = mock_handler
        
        # Act
        result = voice_agent_service.extract_intent("أريد بيتزا")
        
        # Assert
        mock_factory.get_handler.assert_called_once_with("place_order")
        mock_handler.handle.assert_called_once()

def test_extract_intent_should_handle_handler_exception(voice_agent_service):
    # Arrange
    voice_agent_service.intent_service.detect_intent.return_value = '{"intent": "place_order", "items": ["بيتزا"]}'
    
    with patch('services.impl.voice_agent_service_impl.IntentHandlerFactory') as mock_factory:
        mock_handler = MagicMock()
        mock_handler.handle.side_effect = Exception("Handler failed")
        mock_factory.get_handler.return_value = mock_handler
        
        # Act
        result = voice_agent_service.extract_intent("أريد بيتزا")
        
        # Assert
        assert result["intent"] == "unknown"
        assert "عذراً، لم أفهم ما تقصده" in result["reply_text"] 