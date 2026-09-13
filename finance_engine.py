import pandas as pd
from datetime import datetime, timedelta

class FinanceForecaster:
    def forecast_balance(self, start_balance: float, start_date: str, daily_flows: dict, min_balance: float, payment_plan: dict = None, days=90):
        current_date = datetime.strptime(start_date, '%Y-%m-%d')
        balances = []
        current_balance = start_balance
        is_safe = True
        
        for i in range(days):
            date_str = current_date.strftime('%Y-%m-%d')
            flow = daily_flows.get(date_str, 0.0)
            current_balance += flow
            
            if payment_plan and date_str in payment_plan:
                current_balance -= payment_plan[date_str]
                
            balances.append(current_balance)
            if current_balance < min_balance:
                is_safe = False
                
            current_date += timedelta(days=1)
            
        return balances, is_safe

    def compute_amount_safe_to_pay(self, start_balance, start_date, daily_flows, min_balance, requested_amount, days=90):
        # Check if 0 is safe
        _, safe_zero = self.forecast_balance(start_balance, start_date, daily_flows, min_balance, {start_date: 0.0}, days)
        if not safe_zero:
            return 0.0

        low = 0.0
        high = float(requested_amount)
        
        # Check if full amount is safe
        _, safe_full = self.forecast_balance(start_balance, start_date, daily_flows, min_balance, {start_date: high}, days)
        if safe_full:
            return high
            
        # Binary search (precision up to 0.01)
        for _ in range(30):
            mid = (low + high) / 2
            _, safe = self.forecast_balance(start_balance, start_date, daily_flows, min_balance, {start_date: mid}, days)
            if safe:
                low = mid
            else:
                high = mid
                
        ans = round(low, 2)
        _, safe_ans = self.forecast_balance(start_balance, start_date, daily_flows, min_balance, {start_date: ans}, days)
        if not safe_ans:
            ans = round(ans - 0.01, 2)
        return max(0.0, ans)

    def compute_earliest_date(self, start_balance, start_date, daily_flows, min_balance, requested_amount, days=90):
        current_date = datetime.strptime(start_date, '%Y-%m-%d')
        for offset in range(91):
            test_date = (current_date + timedelta(days=offset)).strftime('%Y-%m-%d')
            # Check 90 days from test_date
            _, safe = self.forecast_balance(start_balance, start_date, daily_flows, min_balance, {test_date: requested_amount}, offset + days)
            if safe:
                return test_date
        return None

def build_daily_flows(events_df: pd.DataFrame, start_date: str, days=180) -> dict:
    flows = {}
    if events_df.empty:
        return flows
        
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    
    # Simple recurring extrapolation
    recurring = events_df[events_df['is_recurring'] == True]
    for _, row in recurring.iterrows():
        amount = float(row['amount']) if not pd.isna(row['amount']) else 0.0
        if row.get('type') not in ['salary', 'income', 'deposit', 'refund']:
            amount = -abs(amount)
        else:
            amount = abs(amount)
            
        event_dt = pd.to_datetime(row['event_date'])
        if pd.isna(event_dt): continue
        
        # Extrapolate every 30 days
        for i in range(1, 6):
            next_dt = event_dt + timedelta(days=30*i)
            if next_dt >= start_dt:
                date_str = next_dt.strftime('%Y-%m-%d')
                flows[date_str] = flows.get(date_str, 0.0) + amount
                
    return flows
