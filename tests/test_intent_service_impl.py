import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from services.impl.intent_service_impl import IntentServiceImpl
from unittest.mock import patch, MagicMock

@pytest.fixture
def intent_service():
    service = IntentServiceImpl()
    # Mock the model and tokenizer to avoid heavy computation
    service.model = MagicMock()
    service.tokenizer = MagicMock()
    service.device = MagicMock()
    service.model.generate.return_value = [[1, 2, 3]]
    service.tokenizer.decode.return_value = "mocked_intent"
    return service

def test_detect_intent_should_return_string(intent_service):
    # Arrange
    utterance = "ما هو الوقت المتوقع؟"
    # Act
    result = intent_service.detect_intent(utterance)
    # Assert
    assert isinstance(result, str)
    assert result == "mocked_intent"

def test_detect_intent_should_call_tokenizer_encode(intent_service):
    # Arrange
    utterance = "مرحبا"
    # Mock the tokenizer to return a dict with .to() method
    mock_tokenizer_dict = MagicMock()
    mock_tokenizer_dict.to.return_value = mock_tokenizer_dict
    mock_tokenizer_dict.__getitem__.return_value = MagicMock()  # For inputs["input_ids"]
    
    intent_service.tokenizer.return_value = mock_tokenizer_dict
    # Act
    intent_service.detect_intent(utterance)
    # Assert
    intent_service.tokenizer.assert_called_once()

def test_detect_intent_should_call_model_generate(intent_service):
    # Arrange
    utterance = "أريد طلب"
    # Mock the tokenizer to return a dict with .to() method
    mock_tokenizer_dict = MagicMock()
    mock_tokenizer_dict.to.return_value = mock_tokenizer_dict
    mock_tokenizer_dict.__getitem__.return_value = MagicMock()  # For inputs["input_ids"]
    
    intent_service.tokenizer.return_value = mock_tokenizer_dict
    # Act
    intent_service.detect_intent(utterance)
    # Assert
    intent_service.model.generate.assert_called_once()

def test_detect_intent_should_call_tokenizer_decode(intent_service):
    # Arrange
    utterance = "شكرا لك"
    intent_service.model.generate.return_value = [[4, 5, 6]]
    # Act
    intent_service.detect_intent(utterance)
    # Assert
    intent_service.tokenizer.decode.assert_called_once()

def test_detect_intent_should_handle_empty_utterance(intent_service):
    # Arrange
    utterance = ""
    # Act
    result = intent_service.detect_intent(utterance)
    # Assert
    assert isinstance(result, str)

def test_detect_intent_should_handle_whitespace_utterance(intent_service):
    # Arrange
    utterance = "   "
    # Act
    result = intent_service.detect_intent(utterance)
    # Assert
    assert isinstance(result, str)

def test_detect_intent_should_handle_arabic_text(intent_service):
    # Arrange
    utterance = "أريد دجاج مشوي وعصير"
    # Act
    result = intent_service.detect_intent(utterance)
    # Assert
    assert isinstance(result, str)

def test_detect_intent_should_handle_long_text(intent_service):
    # Arrange
    utterance = "مرحبا، أريد أن أطلب دجاج مشوي مع عصير برتقال، وشكرا لك"
    # Act
    result = intent_service.detect_intent(utterance)
    # Assert
    assert isinstance(result, str)

def test_detect_intent_should_handle_special_characters(intent_service):
    # Arrange
    utterance = "أريد طلب! @#$%"
    # Act
    result = intent_service.detect_intent(utterance)
    # Assert
    assert isinstance(result, str)

def test_detect_intent_should_handle_model_exception(intent_service):
    # Arrange
    utterance = "test"
    intent_service.model.generate.side_effect = Exception("Model error")
    # Act & Assert
    with pytest.raises(Exception):
        intent_service.detect_intent(utterance)

def test_detect_intent_should_handle_tokenizer_exception(intent_service):
    # Arrange
    utterance = "test"
    intent_service.tokenizer.side_effect = Exception("Tokenizer error")
    # Act & Assert
    with pytest.raises(Exception):
        intent_service.detect_intent(utterance)

@patch('services.impl.intent_service_impl.AutoTokenizer.from_pretrained')
@patch('services.impl.intent_service_impl.AutoModelForSeq2SeqLM.from_pretrained')
def test_intent_service_initialization_should_load_model_and_tokenizer(mock_model, mock_tokenizer):
    # Arrange
    mock_tokenizer.return_value = MagicMock()
    mock_model.return_value = MagicMock()
    
    # Act
    service = IntentServiceImpl()
    
    # Assert
    mock_tokenizer.assert_called_once()
    mock_model.assert_called_once()

def test_detect_intent_should_return_json_format(intent_service):
    # Arrange
    utterance = "أريد دجاج مشوي"
    intent_service.tokenizer.decode.return_value = '{"intent": "place_order", "items": ["دجاج مشوي"]}'
    # Act
    result = intent_service.detect_intent(utterance)
    # Assert
    assert isinstance(result, str)
    assert "intent" in result

def test_detect_intent_should_handle_malformed_json_response(intent_service):
    # Arrange
    utterance = "مرحبا"
    intent_service.tokenizer.decode.return_value = "invalid json response"
    # Act
    result = intent_service.detect_intent(utterance)
    # Assert
    assert isinstance(result, str)
    assert result == "invalid json response" 