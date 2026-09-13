import pandas as pd
import sys
import os

def evaluate(output_path, requests_path):
    if not os.path.exists(output_path):
        print("Error: output.csv not found")
        sys.exit(1)
        
    df = pd.read_csv(output_path)
    req_df = pd.read_csv(requests_path)
    
    if len(df) != len(req_df):
        print(f"Row count mismatch: output has {len(df)}, expected {len(req_df)}")
        sys.exit(1)
        
    expected_cols = [
        'request_id', 'amount_safe_to_pay', 'affordability_status', 'recommended_payment_method',
        'payment_plan', 'earliest_date_for_full_payment', 'spending_changes_needed', 'decision_explanation'
    ]
    
    if list(df.columns) != expected_cols:
        print(f"Schema mismatch! Columns: {list(df.columns)}")
        sys.exit(1)
        
    valid_status = ['affordable_now', 'affordable_with_plan', 'affordable_later', 'not_affordable']
    valid_methods = ['full_payment', 'partial_payment', 'installments', 'wait', 'not_recommended']
    
    for _, row in df.iterrows():
        req = req_df[req_df['request_id'] == row['request_id']].iloc[0]
        
        # Schema checks
        if row['affordability_status'] not in valid_status:
            print(f"Invalid status: {row['affordability_status']}")
            sys.exit(1)
        if row['recommended_payment_method'] not in valid_methods:
            print(f"Invalid method: {row['recommended_payment_method']}")
            sys.exit(1)
            
        # Range checks
        safe_amt = float(row['amount_safe_to_pay'])
        req_amt = float(req['requested_amount'])
        if not (0 <= safe_amt <= req_amt):
            print(f"Invalid amount_safe_to_pay for {row['request_id']}: {safe_amt} not in [0, {req_amt}]")
            sys.exit(1)
            
        # Format checks
        # Date formats for earliest_date
        if pd.notna(row['earliest_date_for_full_payment']) and row['earliest_date_for_full_payment'] != "":
            try:
                pd.to_datetime(row['earliest_date_for_full_payment'], format='%Y-%m-%d')
            except ValueError:
                print(f"Invalid earliest date format: {row['earliest_date_for_full_payment']}")
                sys.exit(1)
                
    print("Evaluation passed schema and constraint checks.")

if __name__ == "__main__":
    out_file = sys.argv[1] if len(sys.argv) > 1 else "../output.csv"
    req_file = sys.argv[2] if len(sys.argv) > 2 else "../dataset/requests.csv"
    evaluate(out_file, req_file)
