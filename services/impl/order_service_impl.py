import re
import json
import os
from typing import List, Dict
from difflib import SequenceMatcher
from constants.order_constants import ORDER_KEYWORDS, ORDER_ETA
from constants.app_constants import NAME_EXTRACTION_STOPWORDS, ORDER_EXTRACTION_STOPWORDS, NAME_EXTRACTION_PATTERNS, ARABIC_NUMERALS
import random
from datetime import datetime

class OrderServiceImpl:
    def __init__(self):
        self.orders_file = "orders.json"
        self._ensure_orders_file_exists()

    def _ensure_orders_file_exists(self):
        """Ensure the orders JSON file exists"""
        if not os.path.exists(self.orders_file):
            with open(self.orders_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)

    def _load_orders(self) -> List[Dict]:
        """Load orders from JSON file"""
        try:
            with open(self.orders_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _save_orders(self, orders: List[Dict]):
        """Save orders to JSON file"""
        with open(self.orders_file, 'w', encoding='utf-8') as f:
            json.dump(orders, f, ensure_ascii=False, indent=2)

    def list_orders(self) -> List[Dict]:
        """List all orders from JSON file"""
        return self._load_orders()

    def get_order_by_id(self, order_id: str) -> Dict:
        """Get a specific order by ID"""
        orders = self._load_orders()
        for order in orders:
            if order.get("order_id") == order_id:
                return order
        return None

    @staticmethod
    def extract_order_items(text: str):
        items = []
        
        # First, try to find exact matches in the text
        exact_matches = []
        for menu_item in ORDER_KEYWORDS:
            if menu_item in text:
                exact_matches.append(menu_item)
        
        if exact_matches:
            return exact_matches
        
        # If no exact matches, try to extract items using regex and fuzzy matching
        match = re.search(r'(?:اطلب|أطلب|طلب|عايز|اريد|أريد|بدي|حابب|أحب|أرغب)\s+(.+)', text)
        if match:
            raw_items = re.split(r'[و،,]', match.group(1))
            for item in raw_items:
                item = item.strip()
                if item and len(item) > 2 and item not in ORDER_EXTRACTION_STOPWORDS:
                    words = [w for w in item.split() if w not in ORDER_EXTRACTION_STOPWORDS]
                    cleaned_item = " ".join(words)
                    if cleaned_item and cleaned_item not in ORDER_EXTRACTION_STOPWORDS:
                        # Try to find the best match using fuzzy matching
                        best_match = OrderServiceImpl._find_best_match(cleaned_item, ORDER_KEYWORDS)
                        if best_match:
                            items.append(best_match)
        
        if not items:
            words = text.split()
            for i in range(len(words)):
                for j in range(i + 1, min(i + 4, len(words) + 1)): 
                    candidate = " ".join(words[i:j])
                    if len(candidate) > 2:
                        best_match = OrderServiceImpl._find_best_match(candidate, ORDER_KEYWORDS)
                        if best_match and best_match not in items:
                            items.append(best_match)
        
        return items

    @staticmethod
    def _find_best_match(candidate: str, menu_items: List[str], threshold: float = 0.6) -> str:
        """
        Find the best matching menu item using fuzzy string matching.
        Returns the best match if similarity is above threshold, otherwise None.
        """
        best_match = None
        best_score = 0
        
        for menu_item in menu_items:
            # Calculate similarity using SequenceMatcher
            similarity = SequenceMatcher(None, candidate.lower(), menu_item.lower()).ratio()
            
            # Also check if candidate is a substring of menu item (common for partial transcriptions)
            if candidate.lower() in menu_item.lower():
                similarity = max(similarity, 0.8)  # Boost score for substring matches
            
            # Check if menu item is a substring of candidate (for cases where transcription adds extra words)
            if menu_item.lower() in candidate.lower():
                similarity = max(similarity, 0.9)  # High score for this case
            
            if similarity > best_score and similarity >= threshold:
                best_score = similarity
                best_match = menu_item
        
        return best_match

    @staticmethod
    def extract_name_from_transcription(transcription: str) -> str:
        """
        Extract name from transcription using various patterns
        """
        import re
        
        # Try to match name patterns
        for pattern in NAME_EXTRACTION_PATTERNS:
            match = re.search(pattern, transcription)
            if match:
                return match.group(1).strip()
        
        # If no pattern matches, try to extract the first meaningful word
        # Filter out common words that are not names
        words = transcription.split()
        for word in words:
            if word not in NAME_EXTRACTION_STOPWORDS and len(word) > 1:
                return word
        
        return None


    def process_order_request(self, name: str, items: list, dialog_history: list) -> dict:
        # Extract name if not provided
        if not name:
            name = self.extract_name_from_dialog(dialog_history)
        if not name:
            return {"error": "من فضلك خبرنا باسمك."}
        
        order_id = OrderServiceImpl.generate_arabic_order_id()
        order = {
            "order_id": order_id,
            "name": name,
            "items": items,
            "eta": ORDER_ETA,
            "timestamp": datetime.now().isoformat(),
            "status": "pending"
        }
        
        # Load existing orders, append new order, and save
        orders = self._load_orders()
        orders.append(order)
        self._save_orders(orders)
        
        return order

    def process_order_api_request(self, name: str, items: list, dialog_history: list):
        result = self.process_order_request(name, items, dialog_history)
        if "error" in result:
            return {"error": result["error"]}, 400
        return {"order_id": result["order_id"], "eta": result["eta"]}, 200

    def extract_name_from_dialog(self, dialog_history: list) -> str:
        # Simple heuristic: look for "اسمي" (my name is) or similar in previous messages
        import re
        for message in reversed(dialog_history):
            match = re.search(r"اسمي\s+(\w+)", message)
            if match:
                return match.group(1)
        return None    

    @staticmethod
    def generate_arabic_order_id() -> str:
        """
        Generate a random 5-digit Arabic order ID
        """
        # Generate 5 random digits
        digits = [random.randint(0, 9) for _ in range(5)]
        
        # Convert to Arabic numerals
        arabic_digits = [ARABIC_NUMERALS[digit] for digit in digits]
        
        # Join them together
        return "".join(arabic_digits)    