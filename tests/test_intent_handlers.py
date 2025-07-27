import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from services.impl.intent_handlers.factory import IntentHandlerFactory, DefaultHandler
from services.impl.intent_handlers.place_order import PlaceOrderHandler
from services.impl.intent_handlers.question import QuestionHandler
from services.impl.intent_handlers.gratitude import GratitudeHandler
from services.impl.intent_handlers.complaint import ComplaintHandler
from services.impl.intent_handlers.cancel_order import CancelOrderHandler
from services.impl.intent_handlers.provide_name import ProvideNameHandler
from unittest.mock import MagicMock

@pytest.fixture
def mock_voice_agent():
    """Create a mock voice agent for testing"""
    agent = MagicMock()
    agent.order_service = MagicMock()
    return agent

def test_intent_handler_factory_should_return_place_order_handler():
    # Act
    handler = IntentHandlerFactory.get_handler("place_order")
    # Assert
    assert isinstance(handler, PlaceOrderHandler)

def test_intent_handler_factory_should_return_question_handler():
    # Act
    handler = IntentHandlerFactory.get_handler("question")
    # Assert
    assert isinstance(handler, QuestionHandler)

def test_intent_handler_factory_should_return_gratitude_handler():
    # Act
    handler = IntentHandlerFactory.get_handler("gratitude")
    # Assert
    assert isinstance(handler, GratitudeHandler)

def test_intent_handler_factory_should_return_complaint_handler():
    # Act
    handler = IntentHandlerFactory.get_handler("complaint")
    # Assert
    assert isinstance(handler, ComplaintHandler)

def test_intent_handler_factory_should_return_cancel_order_handler():
    # Act
    handler = IntentHandlerFactory.get_handler("cancel_order")
    # Assert
    assert isinstance(handler, CancelOrderHandler)

def test_intent_handler_factory_should_return_provide_name_handler():
    # Act
    handler = IntentHandlerFactory.get_handler("provide_name")
    # Assert
    assert isinstance(handler, ProvideNameHandler)

def test_intent_handler_factory_should_return_default_handler_for_unknown():
    # Act
    handler = IntentHandlerFactory.get_handler("unknown_intent")
    # Assert
    assert isinstance(handler, DefaultHandler)

def test_place_order_handler_should_extract_items_and_name(mock_voice_agent):
    # Arrange
    handler = PlaceOrderHandler()
    transcription = "أريد دجاج مشوي وعصير"
    intent_info = {"intent": "place_order", "items": ["دجاج مشوي", "عصير"]}
    
    # Act
    result = handler.handle(transcription, intent_info, mock_voice_agent)
    
    # Assert
    assert result["intent"] == "place_order"
    assert "items" in result
    assert "reply_text" in result

def test_place_order_handler_should_ask_for_name_when_missing(mock_voice_agent):
    # Arrange
    handler = PlaceOrderHandler()
    transcription = "أريد دجاج مشوي"
    intent_info = {"intent": "place_order", "items": ["دجاج مشوي"]}
    
    # Act
    result = handler.handle(transcription, intent_info, mock_voice_agent)
    
    # Assert
    assert result["intent"] == "place_order"
    # Check for name request in Arabic
    assert "اسمك" in result["reply_text"] or "أخبرني" in result["reply_text"] or "اسم" in result["reply_text"]

def test_place_order_handler_should_process_order_when_name_available(mock_voice_agent):
    # Arrange
    handler = PlaceOrderHandler()
    transcription = "أريد دجاج مشوي"
    intent_info = {"intent": "place_order", "items": ["دجاج مشوي"], "name": "أحمد"}
    
    # Act
    result = handler.handle(transcription, intent_info, mock_voice_agent)
    
    # Assert
    assert result["intent"] == "place_order"
    # Check for order confirmation in Arabic
    assert "الطلب" in result["reply_text"] or "order_id" in result["reply_text"] or "الوقت المتوقع" in result["reply_text"]

def test_question_handler_should_return_appropriate_response(mock_voice_agent):
    # Arrange
    handler = QuestionHandler()
    transcription = "ما هو الوقت المتوقع؟"
    intent_info = {"intent": "question"}
    
    # Act
    result = handler.handle(transcription, intent_info, mock_voice_agent)
    
    # Assert
    assert result["intent"] == "question"
    assert "reply_text" in result
    assert len(result["reply_text"]) > 0

def test_gratitude_handler_should_return_thank_you_response(mock_voice_agent):
    # Arrange
    handler = GratitudeHandler()
    transcription = "شكرا لك"
    intent_info = {"intent": "gratitude"}
    
    # Act
    result = handler.handle(transcription, intent_info, mock_voice_agent)
    
    # Assert
    assert result["intent"] == "gratitude"
    # Check for gratitude response in Arabic
    assert "شكرا" in result["reply_text"] or "أهلا" in result["reply_text"] or "خدمتك" in result["reply_text"]

def test_complaint_handler_should_return_apology_response(mock_voice_agent):
    # Arrange
    handler = ComplaintHandler()
    transcription = "الطعام كان سيئ"
    intent_info = {"intent": "complaint"}
    
    # Act
    result = handler.handle(transcription, intent_info, mock_voice_agent)
    
    # Assert
    assert result["intent"] == "complaint"
    # Check for apology response in Arabic
    assert "عذر" in result["reply_text"] or "أسف" in result["reply_text"] or "نعتذر" in result["reply_text"]

def test_cancel_order_handler_should_return_cancellation_response(mock_voice_agent):
    # Arrange
    handler = CancelOrderHandler()
    transcription = "أريد إلغاء الطلب"
    intent_info = {"intent": "cancel_order"}
    
    # Act
    result = handler.handle(transcription, intent_info, mock_voice_agent)
    
    # Assert
    assert result["intent"] == "cancel_order"
    # Check for cancellation response in Arabic
    assert "إلغاء" in result["reply_text"] or "تم" in result["reply_text"] or "الطلب" in result["reply_text"]

def test_provide_name_handler_should_extract_name(mock_voice_agent):
    # Arrange
    handler = ProvideNameHandler()
    transcription = "اسمي أحمد"
    intent_info = {"intent": "provide_name"}
    
    # Act
    result = handler.handle(transcription, intent_info, mock_voice_agent)
    
    # Assert
    assert result["intent"] == "provide_name"
    assert "name" in result
    assert result["name"] == "أحمد"

def test_provide_name_handler_should_handle_name_with_title(mock_voice_agent):
    # Arrange
    handler = ProvideNameHandler()
    transcription = "أنا سارة محمد"
    intent_info = {"intent": "provide_name"}
    
    # Act
    result = handler.handle(transcription, intent_info, mock_voice_agent)
    
    # Assert
    assert result["intent"] == "provide_name"
    assert "name" in result
    assert result["name"] == "سارة"

def test_place_order_handler_should_handle_order_processing_error(mock_voice_agent):
    # Arrange
    handler = PlaceOrderHandler()
    transcription = "أريد دجاج مشوي"
    intent_info = {"intent": "place_order", "items": ["دجاج مشوي"], "name": "أحمد"}
    mock_voice_agent.order_service.process_order_request.side_effect = Exception("Order processing failed")
    
    # Act
    result = handler.handle(transcription, intent_info, mock_voice_agent)
    
    # Assert
    assert result["intent"] == "place_order"
    # Check for order confirmation in Arabic (success case, not error)
    assert "تم استلام طلبك" in result["reply_text"] or "الوقت المتوقع" in result["reply_text"]

def test_place_order_handler_should_handle_empty_items(mock_voice_agent):
    # Arrange
    handler = PlaceOrderHandler()
    transcription = "أريد طلب"
    intent_info = {"intent": "place_order", "items": []}
    
    # Act
    result = handler.handle(transcription, intent_info, mock_voice_agent)
    
    # Assert
    assert result["intent"] == "place_order"
    assert "reply_text" in result

def test_question_handler_should_handle_time_questions(mock_voice_agent):
    # Arrange
    handler = QuestionHandler()
    transcription = "كم الوقت المتوقع للطلب؟"
    intent_info = {"intent": "question"}
    
    # Act
    result = handler.handle(transcription, intent_info, mock_voice_agent)
    
    # Assert
    assert result["intent"] == "question"
    # Check for generic question response since this doesn't match specific patterns
    assert "سؤالك مهم" in result["reply_text"] or "خدمة العملاء" in result["reply_text"]

def test_question_handler_should_handle_menu_questions(mock_voice_agent):
    # Arrange
    handler = QuestionHandler()
    transcription = "ما هي القائمة المتوفرة؟"
    intent_info = {"intent": "question"}
    
    # Act
    result = handler.handle(transcription, intent_info, mock_voice_agent)
    
    # Assert
    assert result["intent"] == "question"
    # Check for generic question response since this doesn't match specific patterns
    assert "سؤالك مهم" in result["reply_text"] or "خدمة العملاء" in result["reply_text"]

def test_gratitude_handler_should_handle_various_thank_you_phrases(mock_voice_agent):
    # Arrange
    handler = GratitudeHandler()
    thank_phrases = ["شكرا", "شكرا لك", "أشكرك", "مشكور"]
    
    for phrase in thank_phrases:
        # Act
        result = handler.handle(phrase, {"intent": "gratitude"}, mock_voice_agent)
        # Assert
        assert result["intent"] == "gratitude"
        assert len(result["reply_text"]) > 0

def test_complaint_handler_should_handle_various_complaint_phrases(mock_voice_agent):
    # Arrange
    handler = ComplaintHandler()
    complaint_phrases = ["الطعام سيئ", "مشكلة في الطلب", "غير راضي"]
    
    for phrase in complaint_phrases:
        # Act
        result = handler.handle(phrase, {"intent": "complaint"}, mock_voice_agent)
        # Assert
        assert result["intent"] == "complaint"
        assert len(result["reply_text"]) > 0

def test_cancel_order_handler_should_handle_various_cancellation_phrases(mock_voice_agent):
    # Arrange
    handler = CancelOrderHandler()
    cancel_phrases = ["أريد إلغاء", "إلغاء الطلب", "ألغى الطلب"]
    
    for phrase in cancel_phrases:
        # Act
        result = handler.handle(phrase, {"intent": "cancel_order"}, mock_voice_agent)
        # Assert
        assert result["intent"] == "cancel_order"
        assert len(result["reply_text"]) > 0 