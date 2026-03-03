# import streamlit as st
# import pandas as pd
# from parser import parse_transaction
# from storage import init_db, add_transaction, get_transactions
# from prediction import predict_next_month_expense
# from gpt_helper import get_expense_description
# from gmail_api import fetch_transaction_emails
# from ocr import extract_text_from_image

# st.set_page_config(page_title="BudgetBuddy", page_icon="💰", layout="centered")
# init_db()

# st.markdown(
#     """
#     <h1>Type it like you say it. Let <span style='color:#FF5733; font-weight:bold;'>BudgetBuddy</span> handle the rest.</h1>
#     """,
#     unsafe_allow_html=True
# )

# menu = ["Add Transaction", "Upload Receipt", "Fetch Emails", "View Summary", "Predict Expenses"]
# choice = st.sidebar.selectbox("Menu", menu)

# if choice == "Add Transaction":
#     st.header("Add a New Transaction")
#     user_input = st.text_input("Enter transaction (e.g., 'Spent $25 on coffee')")

#     if st.button("Add Transaction"):
#         if user_input.strip() == "":
#             st.error("Please enter a transaction description.")
#         else:
#             parsed = parse_transaction(user_input)
#             if parsed:
#                 add_transaction(parsed)
#                 st.success(f"Added: {parsed['type'].title()} of ${parsed['amount']:.2f} to category '{parsed['category']}'")
#             else:
#                 st.error("Could not parse the transaction. Please include an amount (e.g., $25).")

# elif choice == "Upload Receipt":
#     st.header("Upload Receipt Image")
#     uploaded_file = st.file_uploader("Choose an image file", type=['png', 'jpg', 'jpeg'])

#     if uploaded_file:
#         with open("temp_receipt.jpg", "wb") as f:
#             f.write(uploaded_file.getbuffer())

#         st.image("temp_receipt.jpg", caption="Uploaded Receipt", use_column_width=True)

#         extracted_text = extract_text_from_image("temp_receipt.jpg")

#         st.subheader("🧾 Extracted Text")
#         st.text(extracted_text)

#         parsed = parse_transaction(extracted_text)
#         if parsed:
#             add_transaction(parsed)
#             st.success(f"✅ Transaction added: {parsed['type'].title()} of ${parsed['amount']:.2f} in category '{parsed['category']}'")

#             if st.button("Explain this with AI 🤖"):
#                 with st.spinner("Thinking..."):
#                     explanation = get_expense_description(parsed['note'], parsed['amount'])
#                     st.info(f"💬 AI Explanation: {explanation}")
#         else:
#             st.warning("❌ Could not parse transaction from the receipt.")

# elif choice == "Fetch Emails":
#     st.header("Fetch Transactions from Gmail")

#     if st.button("Fetch Now"):
#         with st.spinner("Fetching emails..."):
#             new_transactions = fetch_transaction_emails()
#             if new_transactions:
#                 for txn in new_transactions:
#                     add_transaction(txn)
#                 st.success(f"Fetched and added {len(new_transactions)} new transactions!")
#             else:
#                 st.info("No new transactions found or failed to fetch emails.")

# elif choice == "View Summary":
#     st.header("📈 Transaction Summary")

#     transactions = get_transactions()

#     # Make sure transactions is a DataFrame or convert it
#     if transactions is not None:
#         if not isinstance(transactions, pd.DataFrame):
#             try:
#                 transactions = pd.DataFrame(transactions)
#             except Exception as e:
#                 st.error(f"Failed to convert transactions to DataFrame: {e}")
#                 transactions = pd.DataFrame()

#         if not transactions.empty:
#             st.write("### All Transactions")
#             st.dataframe(transactions)

#             st.write("### Total Spend by Category")
#             category_totals = transactions.groupby("category")["amount"].sum().sort_values(ascending=False)
#             st.bar_chart(category_totals)

#             st.write("### Total Spend Over Time")
#             if "date" in transactions.columns:
#                 transactions["date"] = pd.to_datetime(transactions["date"])
#                 time_series = transactions.groupby("date")["amount"].sum()
#                 st.line_chart(time_series)
#         else:
#             st.info("No transactions found.")
#     else:
#         st.info("No transactions found.")


# elif choice == "Predict Expenses":
#     st.header("📉 Expense Prediction")

#     transactions = get_transactions()

#     if transactions is None:
#         st.warning("No transactions to analyze.")
#     else:
#         if not isinstance(transactions, pd.DataFrame):
#             transactions = pd.DataFrame(transactions)

#         if transactions.empty or len(transactions) < 5:
#             st.info("Not enough transactions for prediction.")
#         else:
#             predicted = predict_next_month_expense(transactions)
#             if predicted is None:
#                 st.warning("Not enough data to make a prediction. Please add more transactions.")
#             else:
#                 st.success(f"📅 Estimated expenses for next month: **${predicted:.2f}**")

# ----------------------------------------------------------------------
# app.py (updated)
# import streamlit as st
# import pandas as pd
# import plotly.express as px
# import plotly.graph_objects as go
# from datetime import datetime, timedelta
# from transaction_parser import parse_transaction
# from storage import init_db, add_transaction, get_transactions, get_monthly_summary, set_budget, get_budget
# from prediction import predict_next_month_expense
# from gpt_helper import get_expense_description, get_financial_tips
# from gmail_api import fetch_transaction_emails
# from ocr import extract_text_from_image

# # Page configuration
# st.set_page_config(
#     page_title="BudgetBuddy",
#     page_icon="💰",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # Custom CSS
# st.markdown("""
# <style>
#     .main-header {
#         font-size: 3rem;
#         color: #1f77b4;
#     }
#     .budget-card {
#         border-radius: 10px;
#         padding: 15px;
#         background-color: #f0f2f6;
#         box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
#         margin-bottom: 20px;
#     }
#     .positive {
#         color: #2ecc71;
#     }
#     .negative {
#         color: #e74c3c;
#     }
#     .metric-card {
#         background-color: white;
#         padding: 15px;
#         border-radius: 10px;
#         box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
#     }
# </style>
# """, unsafe_allow_html=True)

# init_db()

# # Initialize session state for user preferences
# if 'dark_mode' not in st.session_state:
#     st.session_state.dark_mode = False

# # Header
# col1, col2 = st.columns([3, 1])
# with col1:
#     st.markdown("<h1 class='main-header'>💰 BudgetBuddy</h1>", unsafe_allow_html=True)
#     st.markdown("### Your Personal Financial Assistant")
# with col2:
#     if st.button("🌙 Dark Mode" if not st.session_state.dark_mode else "☀️ Light Mode"):
#         st.session_state.dark_mode = not st.session_state.dark_mode

# # Navigation
# menu = ["Dashboard", "Add Transaction", "Upload Receipt", "Fetch Emails", 
#         "View Summary", "Budget Planning", "Financial Insights", "Settings"]
# choice = st.sidebar.selectbox("Navigation", menu)

# # Dashboard
# if choice == "Dashboard":
#     st.header("📊 Financial Dashboard")
    
#     # Get transactions and calculate metrics
#     transactions = get_transactions()
#     df = pd.DataFrame(transactions) if transactions else pd.DataFrame()
    
#     if not df.empty:
#         # Calculate metrics
#         current_month = datetime.now().strftime('%Y-%m')
#         monthly_data = df[df['date'].str.startswith(current_month)]
#         total_income = monthly_data[monthly_data['type'] == 'income']['amount'].sum()
#         total_expenses = monthly_data[monthly_data['type'] == 'expense']['amount'].sum()
#         net_flow = total_income - total_expenses
        
#         # Display metrics
#         col1, col2, col3, col4 = st.columns(4)
#         with col1:
#             st.metric("Total Income", f"${total_income:,.2f}")
#         with col2:
#             st.metric("Total Expenses", f"${total_expenses:,.2f}")
#         with col3:
#             st.metric("Net Cash Flow", f"${net_flow:,.2f}", 
#                      delta_color="inverse" if net_flow < 0 else "normal")
#         with col4:
#             # Budget progress (if set)
#             budget = get_budget()
#             if budget:
#                 budget_utilization = (total_expenses / budget) * 100
#                 st.metric("Budget Utilization", f"{budget_utilization:.1f}%")
        
#         # Monthly trends chart
#         st.subheader("Monthly Trends")
#         monthly_summary = get_monthly_summary()
#         if monthly_summary:
#             fig = px.line(monthly_summary, x='month', y='net', title='Monthly Net Cash Flow')
#             st.plotly_chart(fig, use_container_width=True)
        
#         # Recent transactions
#         st.subheader("Recent Transactions")
#         st.dataframe(df.head(10), use_container_width=True)
        
#         # Financial tips from AI
#         with st.expander("💡 Financial Tips"):
#             tips = get_financial_tips(df)
#             st.write(tips)
#     else:
#         st.info("No transactions yet. Add some transactions to see your dashboard.")

# # Other menu options would follow similar enhancements...

# # Budget Planning Page
# elif choice == "Budget Planning":
#     st.header("📋 Budget Planning")
    
#     col1, col2 = st.columns(2)
    
#     with col1:
#         st.subheader("Set Monthly Budget")
#         budget = st.number_input("Monthly Budget ($)", min_value=0.0, step=50.0)
#         if st.button("Save Budget"):
#             set_budget(budget)
#             st.success("Budget saved successfully!")
    
#     with col2:
#         st.subheader("Budget Progress")
#         current_budget = get_budget()
#         if current_budget:
#             transactions = get_transactions()
#             df = pd.DataFrame(transactions) if transactions else pd.DataFrame()
            
#             if not df.empty:
#                 current_month = datetime.now().strftime('%Y-%m')
#                 monthly_expenses = df[(df['date'].str.startswith(current_month)) & 
#                                      (df['type'] == 'expense')]['amount'].sum()
                
#                 progress = min(monthly_expenses / current_budget, 1.0)
#                 st.progress(progress)
#                 st.write(f"${monthly_expenses:,.2f} / ${current_budget:,.2f}")
                
#                 if monthly_expenses > current_budget:
#                     st.error("You've exceeded your budget this month!")
#                 elif progress > 0.8:
#                     st.warning("You're approaching your budget limit.")
#                 else:
#                     st.success("You're within your budget.")
    
#     # Category-wise budget allocation
#     st.subheader("Category-wise Budget Allocation")
#     # Implementation for category budgets would go here

# # Financial Insights Page
# elif choice == "Financial Insights":
#     st.header("🔍 Financial Insights")
    
#     transactions = get_transactions()
#     if transactions:
#         df = pd.DataFrame(transactions)
        
#         # Spending patterns by category
#         st.subheader("Spending Patterns")
#         col1, col2 = st.columns(2)
        
#         with col1:
#             category_spending = df[df['type'] == 'expense'].groupby('category')['amount'].sum()
#             fig = px.pie(values=category_spending.values, names=category_spending.index, 
#                         title="Spending by Category")
#             st.plotly_chart(fig, use_container_width=True)
        
#         with col2:
#             # Weekly spending trends
#             df['date'] = pd.to_datetime(df['date'])
#             df['week'] = df['date'].dt.isocalendar().week
#             weekly_spending = df[df['type'] == 'expense'].groupby('week')['amount'].sum()
#             fig = px.bar(x=weekly_spending.index, y=weekly_spending.values, 
#                         title="Weekly Spending", labels={'x': 'Week', 'y': 'Amount'})
#             st.plotly_chart(fig, use_container_width=True)
        
#         # Expense prediction
#         st.subheader("Future Expense Prediction")
#         predicted = predict_next_month_expense(df)
#         if predicted:
#             st.info(f"Predicted expenses for next month: ${predicted:,.2f}")
            
#             # Compare with historical average
#             historical_avg = df[df['type'] == 'expense'].groupby(
#                 df['date'].dt.to_period('M'))['amount'].sum().mean()
            
#             if predicted > historical_avg * 1.2:
#                 st.warning("Your predicted expenses are significantly higher than your historical average.")
#             elif predicted < historical_avg * 0.8:
#                 st.success("Your predicted expenses are lower than your historical average.")
    
#     else:
#         st.info("No transactions available for insights.")

# # Settings Page
# elif choice == "Settings":
#     st.header("⚙️ Settings")
    
#     st.subheader("Data Management")
#     if st.button("Export Data as CSV"):
#         transactions = get_transactions()
#         if transactions:
#             df = pd.DataFrame(transactions)
#             csv = df.to_csv(index=False)
#             st.download_button(
#                 label="Download CSV",
#                 data=csv,
#                 file_name="budgetbuddy_data.csv",
#                 mime="text/csv"
#             )
    
#     st.subheader("Categories Management")
#     # Allow users to add custom categories
#     new_category = st.text_input("Add New Category")
#     if st.button("Add Category"):
#         # Implementation to add category to database
#         pass
    
#     st.subheader("Notifications")
#     email_notifications = st.checkbox("Enable Email Notifications")
#     budget_alerts = st.checkbox("Enable Budget Alert Notifications")
    
#     if st.button("Save Settings"):
#         st.success("Settings saved successfully!")



# --------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------
# app.py
# import streamlit as st
# import pandas as pd
# import plotly.express as px
# import plotly.graph_objects as go
# from datetime import datetime, timedelta
# import calendar
# from transaction_parser import parse_transaction, CATEGORIES
# from storage import init_db, add_transaction, get_transactions, get_monthly_summary, set_budget, get_budget, update_transaction, delete_transaction, set_savings_goal, get_savings_goal
# from prediction import predict_next_month_expense
# from gpt_helper import get_expense_description, suggest_category
# from gmail_api import fetch_transaction_emails
# from ocr import extract_text_from_image

# # Custom CSS
# st.markdown("""
# <style>
#     .main-header {
#         font-size: 3rem;
#         color: #1f77b4;
#         margin-bottom: 0.5rem;
#     }
#     .sub-header {
#         color: #636363;
#         font-weight: 300;
#         margin-bottom: 2rem;
#     }
#     .budget-card {
#         border-radius: 10px;
#         padding: 15px;
#         background-color: #f0f2f6;
#         box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
#         margin-bottom: 20px;
#     }
#     .positive {
#         color: #2ecc71;
#     }
#     .negative {
#         color: #e74c3c;
#     }
#     .metric-card {
#         background-color: white;
#         padding: 15px;
#         border-radius: 10px;
#         box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
#         height: 100%;
#     }
#     .transaction-table {
#         font-size: 0.9rem;
#     }
#     .category-badge {
#         padding: 4px 8px;
#         border-radius: 12px;
#         font-size: 0.8rem;
#         font-weight: 500;
#     }
#     .progress-bar {
#         height: 10px;
#         border-radius: 5px;
#         background-color: #e0e0e0;
#         margin-top: 5px;
#     }
#     .progress-fill {
#         height: 100%;
#         border-radius: 5px;
#         background-color: #4caf50;
#     }
# </style>
# """, unsafe_allow_html=True)

# # Initialize database
# init_db()

# # Initialize session state
# if 'logged_in' not in st.session_state:
#     st.session_state.logged_in = False
# if 'dark_mode' not in st.session_state:
#     st.session_state.dark_mode = False
# if 'editing_transaction' not in st.session_state:
#     st.session_state.editing_transaction = None

# def apply_theme(dark_mode=False):
#     if dark_mode:
#         st.markdown("""
#         <style>
#             body {
#                 background-color: #0e1117;
#                 color: white;
#             }
#             .main-header {
#                 font-size: 3rem;
#                 color: #f39c12;
#                 margin-bottom: 0.5rem;
#             }
#             .sub-header {
#                 color: #bbbbbb;
#                 font-weight: 300;
#                 margin-bottom: 2rem;
#             }
#             .metric-card {
#                 background-color: #1e222a;
#                 color: white;
#             }
#             .budget-card {
#                 background-color: #1e222a;
#                 color: white;
#             }
#         </style>
#         """, unsafe_allow_html=True)
#     else:
#         st.markdown("""
#         <style>
#             body {
#                 background-color: #ffffff;
#                 color: black;
#             }
#             .main-header {
#                 font-size: 3rem;
#                 color: #1f77b4;
#                 margin-bottom: 0.5rem;
#             }
#             .sub-header {
#                 color: #636363;
#                 font-weight: 300;
#                 margin-bottom: 2rem;
#             }
#             .metric-card {
#                 background-color: white;
#                 color: black;
#             }
#             .budget-card {
#                 background-color: #f0f2f6;
#                 color: black;
#             }
#         </style>
#         """, unsafe_allow_html=True)

# # Simple authentication
# def check_login(username, password):
#     # For demo purposes - in production, use proper authentication
#     return username == "admin" and password == "password"

# # Login section
# if not st.session_state.logged_in:
#     st.markdown("<h1 class='main-header'>💰 BudgetBuddy</h1>", unsafe_allow_html=True)
#     st.markdown("<h3 class='sub-header'>Your Personal Financial Assistant</h3>", unsafe_allow_html=True)
    
#     col1, col2, col3 = st.columns([1, 2, 1])
#     with col2:
#         with st.form("login_form"):
#             username = st.text_input("Username")
#             password = st.text_input("Password", type="password")
#             login_btn = st.form_submit_button("Login")
            
#             if login_btn:
#                 if check_login(username, password):
#                     st.session_state.logged_in = True
#                     st.rerun()
#                 else:
#                     st.error("Invalid username or password")
#     st.stop()

# # Main application
# # Header
# col1, col2, col3 = st.columns([3, 1, 1])

# with col1:
#     if st.session_state.logged_in:
#         st.markdown(
#             """
#             <h1>Type it like you say it. Let <span style='color:#FF5733; font-weight:bold;'>BudgetBuddy</span> handle the rest.</h1>
#             """,
#             unsafe_allow_html=True
#         )

# # with col2:
# #     if st.button("🌙 Dark Mode" if not st.session_state.dark_mode else "☀️ Light Mode"):
# #         st.session_state.dark_mode = not st.session_state.dark_mode
# #         st.rerun()

# # # Apply theme after toggling
# # apply_theme(st.session_state.dark_mode)

# with col3:
#     if st.button("Logout"):
#         st.session_state.logged_in = False
#         st.rerun()

# # Navigation
# menu = ["Dashboard", "Add Transaction", "Upload Receipt", "Fetch Emails", 
#         "View Transactions", "Budget Planning", "Savings Goals", "Financial Insights", "Settings"]
# choice = st.sidebar.selectbox("Navigation", menu)

# # Helper function to get transactions as DataFrame
# def get_transactions_df():
#     transactions = get_transactions()
#     if transactions:
#         df = pd.DataFrame(transactions)
#         if not df.empty:
#             df['date'] = pd.to_datetime(df['date'])
#         return df
#     return pd.DataFrame()

# # Dashboard
# if choice == "Dashboard":
#     st.header("📊 Financial Dashboard")
    
#     # Get transactions and calculate metrics
#     df = get_transactions_df()
    
#     if not df.empty:
#         # Calculate metrics for current month
#         current_month = datetime.now().strftime('%Y-%m')
#         monthly_data = df[df['date'].dt.strftime('%Y-%m') == current_month]
        
#         total_income = monthly_data[monthly_data['type'] == 'income']['amount'].sum()
#         total_expenses = monthly_data[monthly_data['type'] == 'expense']['amount'].sum()
#         net_flow = total_income - total_expenses
        
#         # Display metrics
#         col1, col2, col3, col4 = st.columns(4)
#         with col1:
#             st.markdown('<div class="metric-card">', unsafe_allow_html=True)
#             st.metric("Total Income", f"${total_income:,.2f}")
#             st.markdown('</div>', unsafe_allow_html=True)
#         with col2:
#             st.markdown('<div class="metric-card">', unsafe_allow_html=True)
#             st.metric("Total Expenses", f"${total_expenses:,.2f}")
#             st.markdown('</div>', unsafe_allow_html=True)
#         with col3:
#             st.markdown('<div class="metric-card">', unsafe_allow_html=True)
#             st.metric("Net Cash Flow", f"${net_flow:,.2f}", 
#                      delta_color="inverse" if net_flow < 0 else "normal")
#             st.markdown('</div>', unsafe_allow_html=True)
#         with col4:
#             st.markdown('<div class="metric-card">', unsafe_allow_html=True)
#             # Budget progress (if set)
#             budget = get_budget()
#             if budget:
#                 budget_utilization = (total_expenses / budget) * 100
#                 st.metric("Budget Utilization", f"{budget_utilization:.1f}%")
#             else:
#                 st.metric("Monthly Budget", "Not set")
#             st.markdown('</div>', unsafe_allow_html=True)
        
#         # Charts
#         col1, col2 = st.columns(2)
        
#         with col1:
#             st.subheader("Spending by Category")
#             category_spending = df[df['type'] == 'expense'].groupby('category')['amount'].sum()
#             if not category_spending.empty:
#                 fig = px.pie(values=category_spending.values, names=category_spending.index, 
#                             title="Spending Distribution")
#                 st.plotly_chart(fig, use_container_width=True)
#             else:
#                 st.info("No expense data available")
        
#         with col2:
#             st.subheader("Monthly Trends")
#             monthly_summary = get_monthly_summary()
#             if monthly_summary:
#                 summary_df = pd.DataFrame(monthly_summary)
#                 fig = px.line(summary_df, x='month', y='net', title='Monthly Net Cash Flow')
#                 st.plotly_chart(fig, use_container_width=True)
#             else:
#                 st.info("No monthly summary data available")
        
#         # Recent transactions
#         st.subheader("Recent Transactions")
#         recent_transactions = df.sort_values('date', ascending=False).head(5)
#         for _, row in recent_transactions.iterrows():
#             col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
#             with col1:
#                 st.write(f"{row['note'][:50]}..." if len(row['note']) > 50 else row['note'])
#             with col2:
#                 st.write(row['category'].title())
#             with col3:
#                 amount_color = "positive" if row['type'] == 'income' else "negative"
#                 st.markdown(f"<span class='{amount_color}'>${row['amount']:.2f}</span>", unsafe_allow_html=True)
#             with col4:
#                 st.write(row['date'].strftime('%Y-%m-%d'))
#             st.divider()
        
#         # Financial tips
#         with st.expander("💡 Financial Tips"):
#             # Simple tips based on spending patterns
#             if total_expenses > total_income * 0.7:
#                 st.warning("You're spending more than 70% of your income. Consider reducing expenses in non-essential categories.")
#             elif net_flow > total_income * 0.2:
#                 st.success("Great job! You're saving more than 20% of your income.")
            
#             # Check if any category is over budget
#             if budget:
#                 category_budgets = {}  # This would come from your budget settings
#                 for category, spent in category_spending.items():
#                     if category in category_budgets and spent > category_budgets[category]:
#                         st.warning(f"You've exceeded your budget for {category}.")
#     else:
#         st.info("No transactions yet. Add some transactions to see your dashboard.")

# # Add Transaction Page
# elif choice == "Add Transaction":
#     st.header("💳 Add a New Transaction")
    
#     col1, col2 = st.columns(2)
    
#     with col1:
#         user_input = st.text_input("Enter transaction (e.g., 'Spent $25 on coffee')", 
#                                   placeholder="Spent $25 on coffee at Starbucks")
        
#         if st.button("Parse Transaction"):
#             if user_input.strip() == "":
#                 st.error("Please enter a transaction description.")
#             else:
#                 parsed = parse_transaction(user_input)
#                 if parsed:
#                     # Use AI to suggest category if it's 'other'
#                     if parsed['category'] == 'other':
#                         suggested_category = suggest_category(user_input)
#                         if suggested_category and suggested_category in CATEGORIES:
#                             parsed['category'] = suggested_category
#                             st.success(f"AI suggested category: {suggested_category}")
                    
#                     st.session_state.parsed_transaction = parsed
#                     st.success("Transaction parsed successfully!")
#                 else:
#                     st.error("Could not parse the transaction. Please include an amount (e.g., $25).")
    
#     with col2:
#         if 'parsed_transaction' in st.session_state:
#             parsed = st.session_state.parsed_transaction
            
#             st.subheader("Transaction Details")
#             st.write(f"**Amount:** ${parsed['amount']:.2f}")
#             st.write(f"**Type:** {parsed['type'].title()}")
            
#             # Let user adjust category
#             categories = list(CATEGORIES.keys())
#             selected_category = st.selectbox("Category", categories, 
#                                            index=categories.index(parsed['category']) if parsed['category'] in categories else 0)
            
#             # Let user adjust date
#             transaction_date = st.date_input("Date", datetime.now())
            
#             # Let user add note
#             note = st.text_area("Note", parsed['note'])
            
#             if st.button("Confirm and Add Transaction"):
#                 parsed['category'] = selected_category
#                 parsed['date'] = transaction_date.strftime('%Y-%m-%d %H:%M:%S')
#                 parsed['note'] = note
                
#                 add_transaction(parsed)
#                 del st.session_state.parsed_transaction
#                 st.success(f"Added: {parsed['type'].title()} of ${parsed['amount']:.2f} to category '{parsed['category']}'")

# # Upload Receipt Page
# elif choice == "Upload Receipt":
#     st.header("📸 Upload Receipt Image")
    
#     uploaded_file = st.file_uploader("Choose an image file", type=['png', 'jpg', 'jpeg'])
    
#     if uploaded_file:
#         # Display image
#         st.image(uploaded_file, caption="Uploaded Receipt", use_column_width=True)
        
#         # Extract text
#         with st.spinner("Extracting text from receipt..."):
#             # Save to temp file
#             with open("temp_receipt.jpg", "wb") as f:
#                 f.write(uploaded_file.getbuffer())
            
#             extracted_text = extract_text_from_image("temp_receipt.jpg")
        
#         st.subheader("🧾 Extracted Text")
#         st.text_area("Extracted Text", extracted_text, height=150)
        
#         # Parse transaction
#         if st.button("Parse Receipt"):
#             parsed = parse_transaction(extracted_text)
#             if parsed:
#                 # Use AI to suggest category if it's 'other'
#                 if parsed['category'] == 'other':
#                     suggested_category = suggest_category(extracted_text)
#                     if suggested_category and suggested_category in CATEGORIES:
#                         parsed['category'] = suggested_category
#                         st.success(f"AI suggested category: {suggested_category}")
                
#                 st.session_state.parsed_receipt = parsed
#                 st.success("Transaction parsed from receipt!")
#             else:
#                 st.warning("Could not parse transaction from the receipt.")
    
#     if 'parsed_receipt' in st.session_state:
#         parsed = st.session_state.parsed_receipt
        
#         st.subheader("Transaction Details from Receipt")
#         col1, col2 = st.columns(2)
        
#         with col1:
#             st.write(f"**Amount:** ${parsed['amount']:.2f}")
#             st.write(f"**Type:** {parsed['type'].title()}")
        
#         with col2:
#             # Let user adjust category
#             categories = list(CATEGORIES.keys())
#             selected_category = st.selectbox("Category", categories, 
#                                            index=categories.index(parsed['category']) if parsed['category'] in categories else 0)
            
#             # Let user adjust date
#             transaction_date = st.date_input("Date", datetime.now())
        
#         # Let user add note
#         note = st.text_area("Note", parsed['note'])
        
#         if st.button("Add Transaction from Receipt"):
#             parsed['category'] = selected_category
#             parsed['date'] = transaction_date.strftime('%Y-%m-%d %H:%M:%S')
#             parsed['note'] = note
            
#             add_transaction(parsed)
#             del st.session_state.parsed_receipt
#             st.success(f"Added: {parsed['type'].title()} of ${parsed['amount']:.2f} to category '{parsed['category']}'")
            
#             # AI explanation
#             with st.spinner("Getting AI explanation..."):
#                 explanation = get_expense_description(parsed['note'], parsed['amount'])
#                 st.info(f"💬 AI Explanation: {explanation}")

# # View Transactions Page
# elif choice == "View Transactions":
#     st.header("📋 All Transactions")
    
#     df = get_transactions_df()
    
#     if not df.empty:
#         # Filters
#         col1, col2, col3, col4 = st.columns(4)
        
#         with col1:
#             start_date = st.date_input("Start Date", df['date'].min().date())
#         with col2:
#             end_date = st.date_input("End Date", df['date'].max().date())
#         with col3:
#             categories = ["All"] + list(df['category'].unique())
#             selected_category = st.selectbox("Category", categories)
#         with col4:
#             types = ["All", "Income", "Expense"]
#             selected_type = st.selectbox("Type", types)
        
#         # Apply filters
#         filtered_df = df[(df['date'].dt.date >= start_date) & (df['date'].dt.date <= end_date)]
        
#         if selected_category != "All":
#             filtered_df = filtered_df[filtered_df['category'] == selected_category]
        
#         if selected_type != "All":
#             filtered_df = filtered_df[filtered_df['type'] == selected_type.lower()]
        
#         # Display transactions
#         st.dataframe(
#             filtered_df[['date', 'category', 'type', 'amount', 'note']].rename(columns={
#                 'date': 'Date',
#                 'category': 'Category',
#                 'type': 'Type',
#                 'amount': 'Amount',
#                 'note': 'Description'
#             }),
#             use_container_width=True
#         )
        
#         # Export option
#         csv = filtered_df.to_csv(index=False)
#         st.download_button(
#             label="Export as CSV",
#             data=csv,
#             file_name="transactions.csv",
#             mime="text/csv"
#         )
        
#         # Edit/Delete transactions
#         st.subheader("Edit Transaction")
#         transaction_ids = filtered_df.index.tolist()
#         selected_id = st.selectbox("Select Transaction to Edit", transaction_ids, 
#                                   format_func=lambda x: f"{filtered_df.loc[x, 'date'].strftime('%Y-%m-%d')} - {filtered_df.loc[x, 'note'][:30]}... - ${filtered_df.loc[x, 'amount']:.2f}")
        
#         if selected_id:
#             transaction = filtered_df.loc[selected_id]
            
#             col1, col2 = st.columns(2)
#             with col1:
#                 new_amount = st.number_input("Amount", value=float(transaction['amount']), min_value=0.0, step=1.0)
#             with col2:
#                 new_category = st.selectbox("Category", list(CATEGORIES.keys()), 
#                                           index=list(CATEGORIES.keys()).index(transaction['category']) if transaction['category'] in CATEGORIES else 0)
            
#             new_type = st.selectbox("Type", ["income", "expense"], 
#                                   index=0 if transaction['type'] == 'income' else 1)
#             new_note = st.text_area("Description", transaction['note'])
#             new_date = st.date_input("Date", transaction['date'].date())
            
#             col1, col2 = st.columns(2)
#             with col1:
#                 if st.button("Update Transaction"):
#                     updated_transaction = {
#                         'amount': new_amount,
#                         'category': new_category,
#                         'type': new_type,
#                         'date': new_date.strftime('%Y-%m-%d %H:%M:%S'),
#                         'note': new_note
#                     }
#                     update_transaction(selected_id, updated_transaction)
#                     st.success("Transaction updated successfully!")
#                     st.rerun()
#             with col2:
#                 if st.button("Delete Transaction"):
#                     delete_transaction(selected_id)
#                     st.success("Transaction deleted successfully!")
#                     st.rerun()
#     else:
#         st.info("No transactions found.")

# # Budget Planning Page
# elif choice == "Budget Planning":
#     st.header("📋 Budget Planning")
    
#     col1, col2 = st.columns(2)
    
#     with col1:
#         st.subheader("Set Monthly Budget")
#         budget = st.number_input("Monthly Budget ($)", min_value=0.0, step=50.0, value=get_budget() or 0.0)
#         if st.button("Save Budget"):
#             set_budget(budget)
#             st.success("Budget saved successfully!")
    
#     with col2:
#         st.subheader("Budget Progress")
#         current_budget = get_budget()
#         if current_budget:
#             df = get_transactions_df()
#             if not df.empty:
#                 current_month = datetime.now().strftime('%Y-%m')
#                 monthly_expenses = df[(df['date'].dt.strftime('%Y-%m') == current_month) & 
#                                      (df['type'] == 'expense')]['amount'].sum()
                
#                 progress = min(monthly_expenses / current_budget, 1.0)
#                 st.write(f"${monthly_expenses:,.2f} / ${current_budget:,.2f}")
                
#                 # Progress bar
#                 st.markdown(f"""
#                 <div class="progress-bar">
#                     <div class="progress-fill" style="width: {progress * 100}%"></div>
#                 </div>
#                 """, unsafe_allow_html=True)
                
#                 if monthly_expenses > current_budget:
#                     st.error("You've exceeded your budget this month!")
#                 elif progress > 0.8:
#                     st.warning("You're approaching your budget limit.")
#                 else:
#                     st.success("You're within your budget.")
#             else:
#                 st.info("No expenses this month.")
#         else:
#             st.info("No budget set yet.")
    
#     # Category-wise budget allocation
#     st.subheader("Category-wise Spending")
#     df = get_transactions_df()
#     if not df.empty:
#         category_spending = df[df['type'] == 'expense'].groupby('category')['amount'].sum()
#         if not category_spending.empty:
#             fig = px.bar(x=category_spending.index, y=category_spending.values, 
#                         labels={'x': 'Category', 'y': 'Amount'})
#             st.plotly_chart(fig, use_container_width=True)

# # Savings Goals Page
# elif choice == "Savings Goals":
#     st.header("🎯 Savings Goals")
    
#     col1, col2 = st.columns(2)
    
#     with col1:
#         st.subheader("Set Savings Goal")
#         goal_name = st.text_input("Goal Name", placeholder="e.g., Vacation Fund")
#         target_amount = st.number_input("Target Amount ($)", min_value=1.0, step=50.0)
#         deadline = st.date_input("Target Date", min_value=datetime.now().date())
        
#         if st.button("Set Goal"):
#             if goal_name and target_amount:
#                 set_savings_goal(goal_name, target_amount, deadline.strftime('%Y-%m-%d'))
#                 st.success("Savings goal set successfully!")
#             else:
#                 st.error("Please provide a goal name and target amount.")
    
#     with col2:
#         st.subheader("Current Goals")
#         goals = get_savings_goal()
#         if goals:
#             for goal in goals:
#                 st.markdown(f"**{goal['name']}**")
#                 st.write(f"Target: ${goal['target']:,.2f} by {goal['deadline']}")
                
#                 # Calculate progress (this would need actual savings tracking)
#                 progress = 0.3  # Placeholder - would calculate based on actual savings
#                 st.write(f"Progress: ${goal['target'] * progress:,.2f} / ${goal['target']:,.2f}")
                
#                 # Progress bar
#                 st.markdown(f"""
#                 <div class="progress-bar">
#                     <div class="progress-fill" style="width: {progress * 100}%"></div>
#                 </div>
#                 """, unsafe_allow_html=True)
                
#                 st.divider()
#         else:
#             st.info("No savings goals set yet.")

# # Financial Insights Page
# elif choice == "Financial Insights":
#     st.header("🔍 Financial Insights")
    
#     df = get_transactions_df()
#     if not df.empty:
#         # Spending patterns by category
#         st.subheader("Spending Patterns")
#         col1, col2 = st.columns(2)
        
#         with col1:
#             category_spending = df[df['type'] == 'expense'].groupby('category')['amount'].sum()
#             if not category_spending.empty:
#                 fig = px.pie(values=category_spending.values, names=category_spending.index, 
#                             title="Spending by Category")
#                 st.plotly_chart(fig, use_container_width=True)
        
#         with col2:
#             # Weekly spending trends
#             df['week'] = df['date'].dt.isocalendar().week
#             weekly_spending = df[df['type'] == 'expense'].groupby('week')['amount'].sum()
#             if not weekly_spending.empty:
#                 fig = px.bar(x=weekly_spending.index, y=weekly_spending.values, 
#                             title="Weekly Spending", labels={'x': 'Week', 'y': 'Amount'})
#                 st.plotly_chart(fig, use_container_width=True)
        
#         # Expense prediction
#         st.subheader("Future Expense Prediction")
#         predicted = predict_next_month_expense(df)
#         if predicted:
#             st.info(f"Predicted expenses for next month: **${predicted:,.2f}**")
            
#             # Compare with historical average
#             historical_avg = df[df['type'] == 'expense'].groupby(
#                 df['date'].dt.to_period('M'))['amount'].sum().mean()
            
#             if predicted > historical_avg * 1.2:
#                 st.warning("Your predicted expenses are significantly higher than your historical average.")
#             elif predicted < historical_avg * 0.8:
#                 st.success("Your predicted expenses are lower than your historical average.")
        
#         # Monthly comparison
#         st.subheader("Monthly Comparison")
#         monthly_comparison = df[df['type'] == 'expense'].groupby(
#             df['date'].dt.to_period('M'))['amount'].sum().tail(6)
#         if not monthly_comparison.empty:
#             fig = px.bar(x=monthly_comparison.index.astype(str), y=monthly_comparison.values,
#                         title="Monthly Expenses Comparison", labels={'x': 'Month', 'y': 'Amount'})
#             st.plotly_chart(fig, use_container_width=True)
    
#     else:
#         st.info("No transactions available for insights.")

# # Settings Page
# elif choice == "Settings":
#     st.header("⚙️ Settings")
    
#     st.subheader("Data Management")
#     if st.button("Export All Data as CSV"):
#         df = get_transactions_df()
#         if not df.empty:
#             csv = df.to_csv(index=False)
#             st.download_button(
#                 label="Download CSV",
#                 data=csv,
#                 file_name="budgetbuddy_data.csv",
#                 mime="text/csv"
#             )
#         else:
#             st.warning("No data to export.")
    
#     st.subheader("Categories Management")
#     # Display current categories
#     st.write("Current categories:")
#     for category, keywords in CATEGORIES.items():
#         st.write(f"**{category.title()}**: {', '.join(keywords)}")
    
#     st.subheader("Notifications")
#     email_notifications = st.checkbox("Enable Email Notifications")
#     budget_alerts = st.checkbox("Enable Budget Alert Notifications")
    
#     if st.button("Save Settings"):
#         st.success("Settings saved successfully!")


# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import calendar
import bcrypt
from transaction_parser import parse_transaction, CATEGORIES
from storage import init_db, add_transaction, get_transactions, get_monthly_summary, set_budget, get_budget, update_transaction, delete_transaction, set_savings_goal, get_savings_goal, create_user, verify_user, get_user_settings, set_user_setting
from prediction import predict_next_month_expense
from gpt_helper import get_expense_description, suggest_category
from gmail_api import fetch_transaction_emails
from ocr import extract_text_from_image

# Page configuration
st.set_page_config(
    page_title="BudgetBuddy",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        color: #636363;
        font-weight: 300;
        margin-bottom: 2rem;
    }
    .budget-card {
        border-radius: 10px;
        padding: 15px;
        background-color: #f0f2f6;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    .positive {
        color: #2ecc71;
    }
    .negative {
        color: #e74c3c;
    }
    .metric-card {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        height: 100%;
    }
    .transaction-table {
        font-size: 0.9rem;
    }
    .category-badge {
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    .progress-bar {
        height: 10px;
        border-radius: 5px;
        background-color: #e0e0e0;
        margin-top: 5px;
    }
    .progress-fill {
        height: 100%;
        border-radius: 5px;
        background-color: #4caf50;
    }
    .login-container {
        # max-width: 400px;
        # margin: 0 auto;
        # padding: 20px;
        # border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        background-color: white;
    }
      .hero-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 60px 20px;
        border-radius: 20px;
        margin-bottom: 40px;
        text-align: center;
        color: white;
        position: relative;
        overflow: hidden;
    }
    
    .hero-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="white" opacity="0.1"/><circle cx="75" cy="75" r="1" fill="white" opacity="0.1"/><circle cx="50" cy="50" r="1" fill="white" opacity="0.05"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
        pointer-events: none;
    }
    
    .hero-title {
        font-size: 4rem;
        font-weight: 700;
        margin-bottom: 10px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        position: relative;
        z-index: 1;
    }
    
    .hero-subtitle {
        font-size: 1.3rem;
        opacity: 0.9;
        margin-bottom: 20px;
        position: relative;
        z-index: 1;
    }
    
    .hero-features {
        display: flex;
        justify-content: center;
        gap: 30px;
        margin-top: 30px;
        flex-wrap: wrap;
        position: relative;
        z-index: 1;
    }
    
    .feature-item {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 1rem;
        opacity: 0.95;
    }
    
    .login-container {
        # max-width: 420px;
        # margin: 0 auto;
        # padding: 40px 30px;
        # border-radius: 20px;
        # box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        # background: white;
        # border: 1px solid rgba(255, 255, 255, 0.2);
        # backdrop-filter: blur(10px);
        position: relative;
    }
    
    .login-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #667eea, #764ba2, #f093fb, #f5576c);
        border-radius: 20px 20px 0 0;
    }
    
    .form-header {
        text-align: center;
        margin-bottom: 30px;
    }
    
    .form-title {
        font-size: 2rem;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 8px;
    }
    
    .form-subtitle {
        color: #7f8c8d;
        font-size: 0.95rem;
    }
    
    .stTextInput > div > div > input {
        border-radius: 12px;
        border: 2px solid #e1e8ed;
        padding: 15px 20px;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    .stButton > button {
        width: 100%;
        border-radius: 12px;
        padding: 15px 20px;
        font-size: 1.1rem;
        font-weight: 600;
        margin-top: 10px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        color: white;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
    }
    
    .switch-mode-btn {
        width: 100%;
        padding: 12px 20px;
        border-radius: 12px;
        border: 2px solid #e1e8ed;
        background: white;
        color: #667eea;
        font-weight: 600;
        margin-top: 15px;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .switch-mode-btn:hover {
        border-color: #667eea;
        background: rgba(102, 126, 234, 0.05);
    }
    
    .benefits-section {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 30px;
        margin-top: 50px;
        padding: 0 20px;
    }
    
    .benefit-card {
        text-align: center;
        padding: 30px 20px;
        border-radius: 15px;
        background: white;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
        transition: transform 0.3s ease;
    }
    
    .benefit-card:hover {
        transform: translateY(-5px);
    }
    
    .benefit-icon {
        font-size: 3rem;
        margin-bottom: 15px;
    }
    
    .benefit-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: blueviolet !important;
        margin-bottom: 10px;
    }
    
    .benefit-desc {
        color: #7f8c8d;
        font-size: 0.95rem;
        line-height: 1.5;
    }
    
    .floating-elements {
        position: absolute;
        width: 100%;
        height: 100%;
        overflow: hidden;
        pointer-events: none;
    }
    
    .floating-element {
        position: absolute;
        opacity: 0.1;
        animation: float 6s ease-in-out infinite;
    }
    
    .floating-element:nth-child(1) { top: 10%; left: 10%; animation-delay: 0s; }
    .floating-element:nth-child(2) { top: 20%; right: 10%; animation-delay: 1s; }
    .floating-element:nth-child(3) { bottom: 20%; left: 15%; animation-delay: 2s; }
    .floating-element:nth-child(4) { bottom: 10%; right: 20%; animation-delay: 3s; }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-20px) rotate(180deg); }
    }
    
    .stats-container {
        display: flex;
        justify-content: center;
        gap: 40px;
        margin: 40px 0;
        flex-wrap: wrap;
    }
    
    .stat-item {
        text-align: center;
        color: white;
        position: relative;
        z-index: 1;
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: 700;
        display: block;
    }
    
    .stat-label {
        font-size: 0.9rem;
        opacity: 0.8;
    }
</style>
""", unsafe_allow_html=True)

# Initialize database
init_db()

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False
if 'editing_transaction' not in st.session_state:
    st.session_state.editing_transaction = None
if 'register_mode' not in st.session_state:
    st.session_state.register_mode = False

# Login/Register section
if not st.session_state.logged_in:
    # Hero Section
    st.markdown("""
    <div class="hero-section">
        <div class="floating-elements">
            <div class="floating-element">💰</div>
            <div class="floating-element">💳</div>
            <div class="floating-element">🎯</div>
        </div>
        <h3 class="hero-subtitle">Type it like you say it. Let <span style='color:orange; font-weight:bold;'>BudgetBuddy</span> handle the rest.</h3>
        <div class="stats-container">
            <div class="stat-item">
                <span class="stat-number">100+</span>
                <span class="stat-label">Happy Users</span>
            </div>
            <div class="stat-item">
                <span class="stat-number">95%</span>
                <span class="stat-label">Success Rate</span>
            </div>
        </div>
        <div class="hero-features">
            <div class="feature-item">
                <span>🤖</span>
                <span>AI-Powered Insights</span>
            </div>
            <div class="feature-item">
                <span>📱</span>
                <span>Smart Receipt Scanning</span>
            </div>
            <div class="feature-item">
                <span>🔒</span>
                <span>Bank-Level Security</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        # Toggle between login and register
        if st.session_state.register_mode:
            st.markdown("""
            <div class="form-header">
                <h2 class="form-title">Create Your Account</h2>
                <p class="form-subtitle">Join thousands of users taking control of their finances</p>
            </div>
            """, unsafe_allow_html=True)
            
            with st.form("register_form"):
                new_username = st.text_input("Username", placeholder="Choose a unique username")
                new_password = st.text_input("Password", type="password", placeholder="Create a strong password")
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
                register_btn = st.form_submit_button("🚀 Create Account")
                
                if register_btn:
                    if not new_username or not new_password:
                        st.error("Please enter both username and password")
                    elif new_password != confirm_password:
                        st.error("Passwords do not match")
                    else:
                        user_id = create_user(new_username, new_password)
                        if user_id:
                            st.success("🎉 Account created successfully! Please login.")
                            st.session_state.register_mode = False
                        else:
                            st.error("Username already exists")
            
            st.markdown("""
            <div style="text-align: center; margin-top: 20px;">
                <p style="color: #7f8c8d; margin-bottom: 15px;">Already have an account?</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("← Back to Login"):
                st.session_state.register_mode = False
                st.rerun()
        else:
            st.markdown("""
            <div class="form-header">
                <h2 class="form-title">Welcome Back!</h2>
                <p class="form-subtitle">Sign in to continue your financial journey</p>
            </div>
            """, unsafe_allow_html=True)
            
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="Enter your username")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                login_btn = st.form_submit_button("🔑 Sign In")
                
                if login_btn:
                    if not username or not password:
                        st.error("Please enter both username and password")
                    else:
                        user_id = verify_user(username, password)
                        if user_id:
                            st.session_state.logged_in = True
                            st.session_state.user_id = user_id
                            st.session_state.username = username
                            st.rerun()
                        else:
                            st.error("Invalid username or password")
            
            st.markdown("""
            <div style="text-align: center; margin-top: 20px;">
                <p style="color: #7f8c8d; margin-bottom: 15px;">Don't have an account yet?</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("✨ Create New Account"):
                st.session_state.register_mode = True
                st.rerun()
                
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Benefits Section
    st.markdown("""
    <div class="benefits-section">
        <div class="benefit-card">
            <div class="benefit-icon">🎯</div>
            <h3 class="benefit-title" style='color:#blue'>Smart Goal Setting</h3>
            <p class="benefit-desc">Set and track your financial goals with intelligent recommendations and progress insights.</p>
        </div>
        <div class="benefit-card">
            <div class="benefit-icon">📊</div>
            <h3 class="benefit-title"style='color:#blueviolet'>Advanced Analytics</h3>
            <p class="benefit-desc">Get detailed insights into your spending patterns with beautiful charts and predictions.</p>
        </div>
        <div class="benefit-card">
            <div class="benefit-icon">🤖</div>
            <h3 class="benefit-title" style='color:#blueviolet'>AI Assistant</h3>
            <p class="benefit-desc">Let AI categorize your expenses and provide personalized financial advice.</p>
        </div>
        <div class="benefit-card">
            <div class="benefit-icon">🔒</div>
            <h3 class="benefit-title" style='color:#blueviolet'>Secure & Private</h3>
            <p class="benefit-desc">Your financial data is encrypted and protected with bank-level security measures.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.stop()

# Main application
# Header
col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
with col1:
    st.markdown(f"<h1 class='main-header'>💰 BudgetBuddy</h1>", unsafe_allow_html=True)
    st.markdown(f"<h3 class='sub-header'>Welcome, {st.session_state.username}!</h3>", unsafe_allow_html=True)

with col4:
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.username = None
        st.rerun()

# Navigation
menu = ["Dashboard", "Add Transaction", "Upload Receipt", "Fetch Emails", 
        "View Transactions", "Budget Planning", "Savings Goals", "Financial Insights", "Settings"]
choice = st.sidebar.selectbox("Navigation", menu)

# Helper function to get transactions as DataFrame
def get_transactions_df():
    transactions = get_transactions(st.session_state.user_id)
    if transactions:
        df = pd.DataFrame(transactions)
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
        return df
    return pd.DataFrame()

# Dashboard
if choice == "Dashboard":
    st.header("📊 Financial Dashboard")
    
    # Get transactions and calculate metrics
    df = get_transactions_df()
    
    if not df.empty:
        # Calculate metrics for current month
        current_month = datetime.now().strftime('%Y-%m')
        monthly_data = df[df['date'].dt.strftime('%Y-%m') == current_month]
        
        total_income = monthly_data[monthly_data['type'] == 'income']['amount'].sum()
        total_expenses = monthly_data[monthly_data['type'] == 'expense']['amount'].sum()
        net_flow = total_income - total_expenses
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Total Income", f"${total_income:,.2f}")
            st.markdown('</div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Total Expenses", f"${total_expenses:,.2f}")
            st.markdown('</div>', unsafe_allow_html=True)
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Net Cash Flow", f"${net_flow:,.2f}", 
                     delta_color="inverse" if net_flow < 0 else "normal")
            st.markdown('</div>', unsafe_allow_html=True)
        with col4:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            # Budget progress (if set)
            budget = get_budget(st.session_state.user_id)
            if budget:
                budget_utilization = (total_expenses / budget) * 100
                st.metric("Budget Utilization", f"{budget_utilization:.1f}%")
            else:
                st.metric("Monthly Budget", "Not set")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Spending by Category")
            category_spending = df[df['type'] == 'expense'].groupby('category')['amount'].sum()
            if not category_spending.empty:
                fig = px.pie(values=category_spending.values, names=category_spending.index, 
                            title="Spending Distribution")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No expense data available")
        
        with col2:
            st.subheader("Monthly Trends")
            monthly_summary = get_monthly_summary(st.session_state.user_id)
            if monthly_summary:
                summary_df = pd.DataFrame(monthly_summary)
                fig = px.line(summary_df, x='month', y='net', title='Monthly Net Cash Flow')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No monthly summary data available")
        
        # Recent transactions
        st.subheader("Recent Transactions")
        recent_transactions = df.sort_values('date', ascending=False).head(5)
        for _, row in recent_transactions.iterrows():
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            with col1:
                st.write(f"{row['note'][:50]}..." if len(row['note']) > 50 else row['note'])
            with col2:
                st.write(row['category'].title())
            with col3:
                amount_color = "positive" if row['type'] == 'income' else "negative"
                st.markdown(f"<span class='{amount_color}'>${row['amount']:.2f}</span>", unsafe_allow_html=True)
            with col4:
                st.write(row['date'].strftime('%Y-%m-%d'))
            st.divider()
        
        # Financial tips
        with st.expander("💡 Financial Tips"):
            # Simple tips based on spending patterns
            if total_expenses > total_income * 0.7:
                st.warning("You're spending more than 70% of your income. Consider reducing expenses in non-essential categories.")
            elif net_flow > total_income * 0.2:
                st.success("Great job! You're saving more than 20% of your income.")
            
            # Check if any category is over budget
            if budget:
                category_budgets = {}  # This would come from your budget settings
                for category, spent in category_spending.items():
                    if category in category_budgets and spent > category_budgets[category]:
                        st.warning(f"You've exceeded your budget for {category}.")
    else:
        st.info("No transactions yet. Add some transactions to see your dashboard.")

# Add Transaction Page
elif choice == "Add Transaction":
    st.header("💳 Add a New Transaction")
    
    col1, col2 = st.columns(2)
    
    with col1:
        user_input = st.text_input("Enter transaction (e.g., 'Spent $25 on coffee')", 
                                  placeholder="Spent $25 on coffee at Starbucks")
        
        if st.button("Parse Transaction"):
            if user_input.strip() == "":
                st.error("Please enter a transaction description.")
            else:
                parsed = parse_transaction(user_input)
                if parsed:
                    # Use AI to suggest category if it's 'other'
                    if parsed['category'] == 'other':
                        suggested_category = suggest_category(user_input)
                        if suggested_category and suggested_category in CATEGORIES:
                            parsed['category'] = suggested_category
                            st.success(f"AI suggested category: {suggested_category}")
                    
                    st.session_state.parsed_transaction = parsed
                    st.success("Transaction parsed successfully!")
                else:
                    st.error("Could not parse the transaction. Please include an amount (e.g., $25).")
    
    with col2:
        if 'parsed_transaction' in st.session_state:
            parsed = st.session_state.parsed_transaction
            
            st.subheader("Transaction Details")
            st.write(f"**Amount:** ${parsed['amount']:.2f}")
            st.write(f"**Type:** {parsed['type'].title()}")
            
            # Let user adjust category
            categories = list(CATEGORIES.keys())
            selected_category = st.selectbox("Category", categories, 
                                           index=categories.index(parsed['category']) if parsed['category'] in categories else 0)
            
            # Let user adjust date
            transaction_date = st.date_input("Date", datetime.now())
            
            # Let user add note
            note = st.text_area("Note", parsed['note'])
            
            if st.button("Confirm and Add Transaction"):
                parsed['category'] = selected_category
                parsed['date'] = transaction_date.strftime('%Y-%m-%d %H:%M:%S')
                parsed['note'] = note
                
                add_transaction(st.session_state.user_id, parsed)
                
                del st.session_state.parsed_transaction
                st.success(f"Added: {parsed['type'].title()} of ${parsed['amount']:.2f} to category '{parsed['category']}'")

# Upload Receipt Page
elif choice == "Upload Receipt":
    st.header("📸 Upload Receipt Image")
    
    uploaded_file = st.file_uploader("Choose an image file", type=['png', 'jpg', 'jpeg'])
    
    if uploaded_file:
        # Display image
        st.image(uploaded_file, caption="Uploaded Receipt", use_column_width=True)
        
        # Extract text
        with st.spinner("Extracting text from receipt..."):
            # Save to temp file
            with open("temp_receipt.jpg", "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            extracted_text = extract_text_from_image("temp_receipt.jpg")
        
        st.subheader("🧾 Extracted Text")
        st.text_area("Extracted Text", extracted_text, height=150)
        
        # Parse transaction
        if st.button("Parse Receipt"):
            parsed = parse_transaction(extracted_text)
            if parsed:
                # Use AI to suggest category if it's 'other'
                if parsed['category'] == 'other':
                    suggested_category = suggest_category(extracted_text)
                    if suggested_category and suggested_category in CATEGORIES:
                        parsed['category'] = suggested_category
                        st.success(f"AI suggested category: {suggested_category}")
                
                st.session_state.parsed_receipt = parsed
                st.success("Transaction parsed from receipt!")
            else:
                st.warning("Could not parse transaction from the receipt.")
    
    if 'parsed_receipt' in st.session_state:
        parsed = st.session_state.parsed_receipt
        
        st.subheader("Transaction Details from Receipt")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Amount:** ${parsed['amount']:.2f}")
            st.write(f"**Type:** {parsed['type'].title()}")
        
        with col2:
            # Let user adjust category
            categories = list(CATEGORIES.keys())
            selected_category = st.selectbox("Category", categories, 
                                           index=categories.index(parsed['category']) if parsed['category'] in categories else 0)
            
            # Let user adjust date
            transaction_date = st.date_input("Date", datetime.now())
        
        # Let user add note
        note = st.text_area("Note", parsed['note'])
        
        if st.button("Add Transaction from Receipt"):
            parsed['category'] = selected_category
            parsed['date'] = transaction_date.strftime('%Y-%m-%d %H:%M:%S')
            parsed['note'] = note
            
            add_transaction(st.session_state.user_id, parsed)
            del st.session_state.parsed_receipt
            st.success(f"Added: {parsed['type'].title()} of ${parsed['amount']:.2f} to category '{parsed['category']}'")
            
            # AI explanation
            with st.spinner("Getting AI explanation..."):
                explanation = get_expense_description(parsed['note'], parsed['amount'])
                st.info(f"💬 AI Explanation: {explanation}")

elif choice == "Fetch Emails":
    st.header("Fetch Transactions from Gmail")

    if st.button("Fetch Now"):
        with st.spinner("Fetching emails..."):
            new_transactions = fetch_transaction_emails()
            if new_transactions:
                for txn in new_transactions:
                    add_transaction(txn)
                st.success(f"Fetched and added {len(new_transactions)} new transactions!")
            else:
                st.info("No new transactions found or failed to fetch emails.")

# View Transactions Page
elif choice == "View Transactions":
    st.header("📋 All Transactions")
    
    df = get_transactions_df()
    
    if not df.empty:
        # Filters
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            start_date = st.date_input("Start Date", df['date'].min().date())
        with col2:
            end_date = st.date_input("End Date", df['date'].max().date())
        with col3:
            categories = ["All"] + list(df['category'].unique())
            selected_category = st.selectbox("Category", categories)
        with col4:
            types = ["All", "Income", "Expense"]
            selected_type = st.selectbox("Type", types)
        
        # Apply filters
        filtered_df = df[(df['date'].dt.date >= start_date) & (df['date'].dt.date <= end_date)]
        
        if selected_category != "All":
            filtered_df = filtered_df[filtered_df['category'] == selected_category]
        
        if selected_type != "All":
            filtered_df = filtered_df[filtered_df['type'] == selected_type.lower()]
        
        # Display transactions
        st.dataframe(
            filtered_df[['date', 'category', 'type', 'amount', 'note']].rename(columns={
                'date': 'Date',
                'category': 'Category',
                'type': 'Type',
                'amount': 'Amount',
                'note': 'Description'
            }),
            use_container_width=True
        )
        
        # Export option
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="Export as CSV",
            data=csv,
            file_name="transactions.csv",
            mime="text/csv"
        )
        
        # Edit/Delete transactions
        st.subheader("Edit Transaction")
        transaction_ids = filtered_df.index.tolist()
        selected_id = st.selectbox("Select Transaction to Edit", transaction_ids, 
                                  format_func=lambda x: f"{filtered_df.loc[x, 'date'].strftime('%Y-%m-%d')} - {filtered_df.loc[x, 'note'][:30]}... - ${filtered_df.loc[x, 'amount']:.2f}")
        
        if selected_id:
            transaction = filtered_df.loc[selected_id]
            
            col1, col2 = st.columns(2)
            with col1:
                new_amount = st.number_input("Amount", value=float(transaction['amount']), min_value=0.0, step=1.0)
            with col2:
                new_category = st.selectbox("Category", list(CATEGORIES.keys()), 
                                          index=list(CATEGORIES.keys()).index(transaction['category']) if transaction['category'] in CATEGORIES else 0)
            
            new_type = st.selectbox("Type", ["income", "expense"], 
                                  index=0 if transaction['type'] == 'income' else 1)
            new_note = st.text_area("Description", transaction['note'])
            new_date = st.date_input("Date", transaction['date'].date())
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Update Transaction"):
                    updated_transaction = {
                        'amount': new_amount,
                        'category': new_category,
                        'type': new_type,
                        'date': new_date.strftime('%Y-%m-%d %H:%M:%S'),
                        'note': new_note
                    }
                    update_transaction(st.session_state.user_id, selected_id, updated_transaction)
                    st.success("Transaction updated successfully!")
                    st.rerun()
            with col2:
                if st.button("Delete Transaction"):
                    delete_transaction(st.session_state.user_id, selected_id)
                    st.success("Transaction deleted successfully!")
                    st.rerun()
    else:
        st.info("No transactions found.")

# Budget Planning Page
elif choice == "Budget Planning":
    st.header("📋 Budget Planning")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Set Monthly Budget")
        budget = st.number_input("Monthly Budget ($)", min_value=0.0, step=50.0, value=get_budget(st.session_state.user_id) or 0.0)
        if st.button("Save Budget"):
            set_budget(st.session_state.user_id, budget)
            st.success("Budget saved successfully!")
    
    with col2:
        st.subheader("Budget Progress")
        current_budget = get_budget(st.session_state.user_id)
        if current_budget:
            df = get_transactions_df()
            if not df.empty:
                current_month = datetime.now().strftime('%Y-%m')
                monthly_expenses = df[(df['date'].dt.strftime('%Y-%m') == current_month) & 
                                     (df['type'] == 'expense')]['amount'].sum()
                
                progress = min(monthly_expenses / current_budget, 1.0)
                st.write(f"${monthly_expenses:,.2f} / ${current_budget:,.2f}")
                
                # Progress bar
                st.markdown(f"""
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {progress * 100}%"></div>
                </div>
                """, unsafe_allow_html=True)
                
                if monthly_expenses > current_budget:
                    st.error("You've exceeded your budget this month!")
                elif progress > 0.8:
                    st.warning("You're approaching your budget limit.")
                else:
                    st.success("You're within your budget.")
            else:
                st.info("No expenses this month.")
        else:
            st.info("No budget set yet.")
    
    # Category-wise budget allocation
    st.subheader("Category-wise Spending")
    df = get_transactions_df()
    if not df.empty:
        category_spending = df[df['type'] == 'expense'].groupby('category')['amount'].sum()
        if not category_spending.empty:
            fig = px.bar(x=category_spending.index, y=category_spending.values, 
                        labels={'x': 'Category', 'y': 'Amount'})
            st.plotly_chart(fig, use_container_width=True)

# Savings Goals Page
elif choice == "Savings Goals":
    st.header("🎯 Savings Goals")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Set Savings Goal")
        goal_name = st.text_input("Goal Name", placeholder="e.g., Vacation Fund")
        target_amount = st.number_input("Target Amount ($)", min_value=1.0, step=50.0)
        deadline = st.date_input("Target Date", min_value=datetime.now().date())
        
        if st.button("Set Goal"):
            if goal_name and target_amount:
                set_savings_goal(st.session_state.user_id, goal_name, target_amount, deadline.strftime('%Y-%m-%d'))
                st.success("Savings goal set successfully!")
            else:
                st.error("Please provide a goal name and target amount.")
    
    with col2:
        st.subheader("Current Goals")
        goals = get_savings_goal(st.session_state.user_id)
        if goals:
            for goal in goals:
                st.markdown(f"**{goal['name']}**")
                st.write(f"Target: ${goal['target']:,.2f} by {goal['deadline']}")
                
                # Calculate progress (this would need actual savings tracking)
                progress = 0.3  # Placeholder - would calculate based on actual savings
                st.write(f"Progress: ${goal['target'] * progress:,.2f} / ${goal['target']:,.2f}")
                
                # Progress bar
                st.markdown(f"""
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {progress * 100}%"></div>
                </div>
                """, unsafe_allow_html=True)
                
                st.divider()
        else:
            st.info("No savings goals set yet.")

# Financial Insights Page
elif choice == "Financial Insights":
    st.header("🔍 Financial Insights")
    
    df = get_transactions_df()
    if not df.empty:
        # Spending patterns by category
        st.subheader("Spending Patterns")
        col1, col2 = st.columns(2)
        
        with col1:
            category_spending = df[df['type'] == 'expense'].groupby('category')['amount'].sum()
            if not category_spending.empty:
                fig = px.pie(values=category_spending.values, names=category_spending.index, 
                            title="Spending by Category")
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Weekly spending trends
            df['week'] = df['date'].dt.isocalendar().week
            weekly_spending = df[df['type'] == 'expense'].groupby('week')['amount'].sum()
            if not weekly_spending.empty:
                fig = px.bar(x=weekly_spending.index, y=weekly_spending.values, 
                            title="Weekly Spending", labels={'x': 'Week', 'y': 'Amount'})
                st.plotly_chart(fig, use_container_width=True)
        
        # Expense prediction
        st.subheader("Future Expense Prediction")
        predicted = predict_next_month_expense(df)
        if predicted:
            st.info(f"Predicted expenses for next month: **${predicted:,.2f}**")
            
            # Compare with historical average
            historical_avg = df[df['type'] == 'expense'].groupby(
                df['date'].dt.to_period('M'))['amount'].sum().mean()
            
            if predicted > historical_avg * 1.2:
                st.warning("Your predicted expenses are significantly higher than your historical average.")
            elif predicted < historical_avg * 0.8:
                st.success("Your predicted expenses are lower than your historical average.")
        
        # Monthly comparison
        st.subheader("Monthly Comparison")
        monthly_comparison = df[df['type'] == 'expense'].groupby(
            df['date'].dt.to_period('M'))['amount'].sum().tail(6)
        if not monthly_comparison.empty:
            fig = px.bar(x=monthly_comparison.index.astype(str), y=monthly_comparison.values,
                        title="Monthly Expenses Comparison", labels={'x': 'Month', 'y': 'Amount'})
            st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.info("No transactions available for insights.")

# Settings Page
elif choice == "Settings":
    st.header("⚙️ Settings")
    
    st.subheader("Data Management")
    if st.button("Export All Data as CSV"):
        df = get_transactions_df()
        if not df.empty:
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="budgetbuddy_data.csv",
                mime="text/csv"
            )
        else:
            st.warning("No data to export.")
    
    st.subheader("Categories Management")
    # Display current categories
    st.write("Current categories:")
    for category, keywords in CATEGORIES.items():
        st.write(f"**{category.title()}**: {', '.join(keywords)}")
    
    st.subheader("Notifications")
    email_notifications = st.checkbox("Enable Email Notifications")
    budget_alerts = st.checkbox("Enable Budget Alert Notifications")
    
    if st.button("Save Settings"):
        set_user_setting(st.session_state.user_id, "email_notifications", str(email_notifications))
        set_user_setting(st.session_state.user_id, "budget_alerts", str(budget_alerts))
        st.success("Settings saved successfully!")