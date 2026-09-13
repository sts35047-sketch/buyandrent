import pandas as pd
import json

def generate_js():
    try:
        requests = pd.read_csv('dataset/requests.csv')
        output = pd.read_csv('output.csv')
        events = pd.read_csv('dataset/financial_events.csv')
        
        # Take the first request for the dashboard
        req = requests.iloc[0]
        out = output.iloc[0]
        user_id = req['user_id']
        
        # Get transactions for this user
        user_events = events[events['user_id'] == user_id].head(5)
        txs = []
        for _, e in user_events.iterrows():
            txs.append({
                'name': e['description'],
                'category': e['event_type'],
                'date': e['event_date'],
                'amount': float(e['amount']),
                'dot': '#5B5CFF' if float(e['amount']) > 0 else '#FF4D3E'
            })
            
        data = {
            'item_name': 'Hackathon Request',
            'item_desc': req['request_text'],
            'amount': float(req['requested_amount']),
            'affordability': out['affordability_status'],
            'payment_method': out['recommended_payment_method'],
            'decision_explanation': out['decision_explanation'],
            'safe_to_pay': float(out['amount_safe_to_pay']),
            'transactions': txs
        }
        
        with open('dashboard_data.js', 'w') as f:
            f.write(f"window.HACKATHON_DATA = {json.dumps(data)};")
            
        print("Generated dashboard_data.js successfully!")
    except Exception as e:
        print(f"Error generating data: {e}")

if __name__ == '__main__':
    generate_js()
