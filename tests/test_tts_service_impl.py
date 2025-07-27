import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from services.impl.tts_service_impl import TTSServiceImpl
from unittest.mock import patch, MagicMock
import tempfile

@pytest.fixture
def tts_service():
    return TTSServiceImpl()

@patch('services.impl.tts_service_impl.requests.post')
def test_synthesize_speech_should_return_bytes_when_success(mock_post):
    # Arrange
    mock_response = MagicMock()
    mock_response.content = b'audio-bytes'
    mock_response.raise_for_status = MagicMock()
    mock_post.return_value = mock_response
    service = TTSServiceImpl()
    
    # Act
    result = service.synthesize_speech('hello')
    
    # Assert
    assert isinstance(result, bytes)
    assert result == b'audio-bytes'
    
    # Verify the API call was made correctly
    mock_post.assert_called_once()
    call_args = mock_post.call_args
    assert 'xi-api-key' in call_args[1]['headers']
    assert call_args[1]['json']['text'] == 'hello'

@patch('services.impl.tts_service_impl.requests.post')
def test_synthesize_speech_should_raise_exception_on_timeout(mock_post):
    # Arrange
    mock_post.side_effect = Exception('API timeout')
    service = TTSServiceImpl()
    
    # Act & Assert
    with pytest.raises(Exception):
        service.synthesize_speech('hello')

@patch('services.impl.tts_service_impl.requests.post')
def test_synthesize_speech_should_raise_exception_on_connection_error(mock_post):
    # Arrange
    from requests.exceptions import ConnectionError
    mock_post.side_effect = ConnectionError('Connection failed')
    service = TTSServiceImpl()
    
    # Act & Assert
    with pytest.raises(ConnectionError):
        service.synthesize_speech('hello')

@patch('services.impl.tts_service_impl.requests.post')
def test_synthesize_speech_should_raise_exception_on_request_error(mock_post):
    # Arrange
    from requests.exceptions import RequestException
    mock_post.side_effect = RequestException('Request failed')
    service = TTSServiceImpl()
    
    # Act & Assert
    with pytest.raises(RequestException):
        service.synthesize_speech('hello')

@patch('services.impl.tts_service_impl.requests.post')
def test_synthesize_speech_should_use_correct_voice_settings(mock_post):
    # Arrange
    mock_response = MagicMock()
    mock_response.content = b'audio-bytes'
    mock_response.raise_for_status = MagicMock()
    mock_post.return_value = mock_response
    service = TTSServiceImpl()
    
    # Act
    service.synthesize_speech('test text')
    
    # Assert
    call_args = mock_post.call_args
    voice_settings = call_args[1]['json']['voice_settings']
    assert voice_settings['stability'] == 0.5
    assert voice_settings['similarity_boost'] == 0.75

@patch('services.impl.tts_service_impl.requests.post')
def test_synthesize_speech_should_use_timeout(mock_post):
    # Arrange
    mock_response = MagicMock()
    mock_response.content = b'audio-bytes'
    mock_response.raise_for_status = MagicMock()
    mock_post.return_value = mock_response
    service = TTSServiceImpl()
    
    # Act
    service.synthesize_speech('test text')
    
    # Assert
    call_args = mock_post.call_args
    assert call_args[1]['timeout'] == 30

def test_environment_variables_should_be_loaded():
    """Test that environment variables are properly loaded with fallbacks"""
    from services.impl.tts_service_impl import ELEVENLABS_API_KEY, VOICE_ID
    
    # Should have fallback values even if .env file doesn't exist
    assert ELEVENLABS_API_KEY is not None
    assert VOICE_ID is not None
    assert len(ELEVENLABS_API_KEY) > 0
    assert len(VOICE_ID) > 0

@patch('services.impl.tts_service_impl.load_dotenv')
def test_load_dotenv_should_handle_missing_env_file(mock_load_dotenv):
    """Test that missing .env file is handled gracefully"""
    mock_load_dotenv.side_effect = Exception("File not found")
    
    # Should not raise an exception
    service = TTSServiceImpl()
    assert service is not None 