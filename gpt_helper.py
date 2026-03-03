# import os
# import openai

# openai.api_key = os.getenv("OPENAI_API_KEY")

# def get_expense_description(transaction_note, amount):
#     prompt = f"Explain this transaction in a friendly way: '{transaction_note}', amount: ${amount:.2f}"
#     response = openai.Completion.create(
#         model="text-davinci-003",
#         prompt=prompt,
#         max_tokens=50,
#         temperature=0.7,
#     )
#     return response.choices[0].text.strip()

# if __name__ == "__main__":
#     print(get_expense_description("Bought groceries at Target", 72))
# --------------------------------------------------------------------



# gpt_helper.py (enhanced)
# import os
# import openai
# import json

# openai.api_key = os.getenv("OPENAI_API_KEY")

# def get_financial_tips(transactions_df):
#     # Convert groupby result to JSON-safe summary
#     summary_df = transactions_df.groupby(['type', 'category'])['amount'].sum().reset_index()
#     summary = summary_df.to_dict(orient='records')

#     prompt = f"""
#     Based on the following financial summary: {json.dumps(summary)}
#     Provide 3 personalized financial tips in a concise, actionable format.
#     """

#     try:
#         response = openai.ChatCompletion.create(
#             model="gpt-3.5-turbo",
#             messages=[
#                 {"role": "system", "content": "You are a helpful financial advisor."},
#                 {"role": "user", "content": prompt}
#             ],
#             max_tokens=150,
#             temperature=0.7,
#         )
#         return response.choices[0].message.content.strip()
#     except Exception as e:
#         print(f"[GPT Error] {e}")
#         return "Here are some general tips: 1. Track your expenses regularly. 2. Set a monthly budget. 3. Review your spending patterns monthly."

# def get_expense_analysis(transactions_df):
#     # More detailed analysis of expenses
#     pass

# def get_expense_description(transaction_note, amount):
#     prompt = f"Explain this transaction in a friendly way: '{transaction_note}', amount: ${amount:.2f}"
#     response = openai.Completion.create(
#         model="text-davinci-003",
#         prompt=prompt,
#         max_tokens=50,
#         temperature=0.7,
#     )
#     return response.choices[0].text.strip()





# -----------------------------------------------------------------




# gpt_helper.py
# import os
# import openai

# openai.api_key = os.getenv("OPENAI_API_KEY")

# def get_expense_description(transaction_note, amount):
#     prompt = f"Explain this transaction in a friendly way: '{transaction_note}', amount: ${amount:.2f}"
#     try:
#         response = openai.Completion.create(
#             model="text-davinci-003",
#             prompt=prompt,
#             max_tokens=50,
#             temperature=0.7,
#         )
#         return response.choices[0].text.strip()
#     except:
#         return "This appears to be a routine transaction."

# def suggest_category(transaction_text):
#     prompt = f"""Categorize this transaction: '{transaction_text}'
#     Choose from: food, utilities, income, transport, entertainment, shopping, other
#     Respond with just the category name:"""
    
#     try:
#         response = openai.Completion.create(
#             model="text-davinci-003",
#             prompt=prompt,
#             max_tokens=10,
#             temperature=0.3,
#         )
#         category = response.choices[0].text.strip().lower()
#         return category if category in ['food', 'utilities', 'income', 'transport', 'entertainment', 'shopping', 'other'] else 'other'
#     except:
#         return 'other'
    
    
    
    
    
    
    # gpt_helper.py
import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

def get_expense_description(transaction_note, amount):
    prompt = f"Explain this transaction in a friendly way: '{transaction_note}', amount: ${amount:.2f}"
    try:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=50,
            temperature=0.7,
        )
        return response.choices[0].text.strip()
    except:
        return "This appears to be a routine transaction."

def suggest_category(transaction_text):
    prompt = f"""Categorize this transaction: '{transaction_text}'
    Choose from: food, utilities, income, transport, entertainment, shopping, other
    Respond with just the category name:"""
    
    try:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=10,
            temperature=0.3,
        )
        category = response.choices[0].text.strip().lower()
        return category if category in ['food', 'utilities', 'income', 'transport', 'entertainment', 'shopping', 'other'] else 'other'
    except:
        return 'other'