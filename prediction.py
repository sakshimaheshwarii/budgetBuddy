import sqlite3
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import datetime
import pandas as pd
import calendar
DB_NAME = 'budgetbuddy.db'

def get_monthly_expenses():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT date, amount FROM transactions WHERE type="expense" ORDER BY date')
    rows = c.fetchall()
    conn.close()

    monthly = {}
    for d, amt in rows:
        month = datetime.strptime(d, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m')
        monthly[month] = monthly.get(month, 0) + amt
    return monthly

def predict_next_month_expense(transactions):
    # Preprocess input DataFrame
    if transactions.empty:
        return None

    # Filter expenses only
    expenses = transactions[transactions['type'] == 'expense']

    if expenses.empty:
        return None

    # Parse month from date
    expenses['month'] = pd.to_datetime(expenses['date']).dt.to_period('M').astype(str)
    monthly = expenses.groupby('month')['amount'].sum().to_dict()

    if len(monthly) < 2:
        return None

    months = sorted(monthly.keys())
    X = np.array(range(len(months))).reshape(-1, 1)
    y = np.array([monthly[m] for m in months])

    model = LinearRegression()
    model.fit(X, y)

    next_month = len(months)
    pred = model.predict([[next_month]])
    return max(pred[0], 0)
