DEFAULT_REPLY = "عذرًا، لم أفهم ما تقصده."
ORDER_ETA = "15 دقيقة"
CUSTOMER_SERVICE_NUMBER = "123456789"
CUSTOMER_SERVICE_HOURS = "ساعات خدمة العملاء من 10 صباحاً حتى 11 مساءً يومياً."
CUSTOMER_SERVICE_ADDRESS = "شارع الثورة، دمشق، سوريا."
MENU_KEYWORDS = ["قائمة", "أطباق", "متوفر", "قائمة الطعام", "الطعام", "أكلات", "ماذا عندكم", "اعرف"]
GREETING_KEYWORDS = ["مرحبا", "أهلا", "السلام عليكم", "صباح الخير", "مساء الخير"] 
API_URL = "http://localhost:5050"

# Stopwords for name extraction
NAME_EXTRACTION_STOPWORDS = {
    "ان", "أن", "اطلب", "أطلب", "طلب", "عايز", "اريد", "أريد", "بدي", 
    "حابب", "أحب", "أرغب", "من", "لو", "ممكن", "اسمي", "أنا", "ضيف", 
    "الطلب", "باسم"
}

# Stopwords for order extraction
ORDER_EXTRACTION_STOPWORDS = {
    "ان", "أن", "اطلب", "أطلب", "طلب", "عايز", "اريد", "أريد", "بدي", 
    "حابب", "أحب", "أرغب", "من", "لو", "ممكن"
}

# Name extraction patterns
NAME_EXTRACTION_PATTERNS = [
    r"اسمي\s+(\w+)",  # "اسمي أحمد"
    r"أنا\s+(\w+)",   # "أنا أحمد"
    r"اسمي\s+(\w+\s+\w+)",  # "اسمي أحمد محمد"
    r"أنا\s+(\w+\s+\w+)",   # "أنا أحمد محمد"
    r"ضيف\s+الطلب\s+باسم\s+(\w+)",  # "ضيف الطلب باسم أحمد"
    r"الطلب\s+باسم\s+(\w+)",  # "الطلب باسم أحمد"
]

# Arabic numerals mapping
ARABIC_NUMERALS = {
    0: "٠", 1: "١", 2: "٢", 3: "٣", 4: "٤",
    5: "٥", 6: "٦", 7: "٧", 8: "٨", 9: "٩"
}