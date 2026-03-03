# import re
# import datetime

# CATEGORIES = {
#     'food': ['subway', 'pizza', 'restaurant', 'burger', 'coffee', 'lunch', 'dinner', 'breakfast'],
#     'utilities': ['electricity', 'water', 'internet', 'gas', 'phone', 'utility'],
#     'income': ['salary', 'bonus', 'refund', 'paycheck'],
#     'transport': ['uber', 'taxi', 'bus', 'train', 'flight', 'car'],
#     'entertainment': ['movie', 'netflix', 'game', 'concert', 'netflix'],
#     'shopping': ['amazon', 'target', 'walmart', 'clothes', 'shopping'],
# }

# def parse_transaction(text):
#     amount_match = re.search(r'(\$)?(\d+(\.\d{1,2})?)', text)
#     if not amount_match:
#         return None

#     amount = float(amount_match.group(2))

#     transaction_type = 'expense'
#     lowered = text.lower()
#     if any(word in lowered for word in CATEGORIES['income']):
#         transaction_type = 'income'

#     category = 'other'
#     for cat, keywords in CATEGORIES.items():
#         if any(word in lowered for word in keywords):
#             category = cat
#             break

#     return {
#         'amount': amount,
#         'category': category,
#         'type': transaction_type,
#         'date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
#         'note': text
#     }
# -------------------------------------------------

# parser.py (enhanced)
# import re
# import datetime
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.naive_bayes import MultinomialNB
# import joblib
# import os

# # ... existing code ...

# # Train a simple ML model for category classification
# def train_category_classifier():
#     # This would be trained on a dataset of transaction descriptions
#     # For now, we'll use a simple implementation
#     pass

# def parse_transaction(text):
#     # First try the rule-based approach
#     parsed = parse_transaction(text)
#     if parsed and parsed['category'] != 'other':
#         return parsed
    
#     # If rule-based fails, try ML approach
#     # Load pre-trained model (if exists)
#     if os.path.exists('category_model.pkl'):
#         vectorizer = joblib.load('category_vectorizer.pkl')
#         model = joblib.load('category_model.pkl')
        
#         # Transform text and predict
#         X = vectorizer.transform([text])
#         predicted_category = model.predict(X)[0]
        
#         parsed['category'] = predicted_category
#         return parsed
    
#     return parsed


# ------------------------------------------

import re
import datetime
import os
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

CATEGORIES = {
    'food': ['subway', 'pizza', 'restaurant', 'burger', 'coffee', 'lunch', 'dinner', 'breakfast'],
    'utilities': ['electricity', 'water', 'internet', 'gas', 'phone', 'utility'],
    'income': ['salary', 'bonus', 'refund', 'paycheck'],
    'transport': ['uber', 'taxi', 'bus', 'train', 'flight', 'car'],
    'entertainment': ['movie', 'netflix', 'game', 'concert'],
    'shopping': ['amazon', 'target', 'walmart', 'clothes', 'shopping'],
}

def rule_based_parse_transaction(text):
    amount_match = re.search(r'(\$)?(\d+(\.\d{1,2})?)', text)
    if not amount_match:
        return None

    amount = float(amount_match.group(2))

    transaction_type = 'expense'
    lowered = text.lower()
    if any(word in lowered for word in CATEGORIES['income']):
        transaction_type = 'income'

    category = 'other'
    for cat, keywords in CATEGORIES.items():
        if any(word in lowered for word in keywords):
            category = cat
            break

    return {
        'amount': amount,
        'category': category,
        'type': transaction_type,
        'date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'note': text
    }

def parse_transaction(text):
    # First try the rule-based approach
    parsed = rule_based_parse_transaction(text)
    if parsed and parsed['category'] != 'other':
        return parsed
    
    # If rule-based fails or category == 'other', try ML fallback
    if os.path.exists('category_model.pkl') and os.path.exists('category_vectorizer.pkl'):
        vectorizer = joblib.load('category_vectorizer.pkl')
        model = joblib.load('category_model.pkl')
        
        X = vectorizer.transform([text])
        predicted_category = model.predict(X)[0]
        
        if parsed is None:
            # No amount detected, can't proceed well, so return None
            return None
        
        parsed['category'] = predicted_category
        return parsed
    
    return parsed
