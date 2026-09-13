import pandas as pd
from datetime import datetime, timedelta

def get_completion_date(plan_str, start_date):
    if not plan_str or plan_str == 'none':
        return start_date
    parts = plan_str.split('|')
    last_payment = parts[-1].split(':')[0]
    return last_payment

def get_start_date(plan_str, start_date):
    if not plan_str or plan_str == 'none':
        return start_date
    parts = plan_str.split('|')
    first_payment = parts[0].split(':')[0]
    return first_payment

def get_num_payments(plan_str):
    if not plan_str or plan_str == 'none':
        return 0
    return len(plan_str.split('|'))

def format_amt(amt):
    s = f"{round(amt, 2):.2f}"
    if s.endswith('.00'):
        return s[:-3]
    if s[-1] == '0':
        return s[:-1]
    return s

def rank_payment_options(options, start_balance, start_date, daily_flows, min_balance, requested_amount, forecaster, profile, req_metadata, spending_changes="none"):
    candidates = []
    
    allowed_methods = []
    if 'payment_methods_user_will_consider' in profile and not pd.isna(profile['payment_methods_user_will_consider']):
        allowed_methods = [x.strip() for x in str(profile['payment_methods_user_will_consider']).split('|')]

    desired_date = req_metadata['desired_completion_date']
    allows_partial = str(req_metadata.get('allows_partial_payment', 'false')).lower() == 'true'

    safe_amt = forecaster.compute_amount_safe_to_pay(start_balance, start_date, daily_flows, min_balance, requested_amount)
    earliest = forecaster.compute_earliest_date(start_balance, start_date, daily_flows, min_balance, requested_amount)

    # 1. full_payment
    full_safe = safe_amt >= requested_amount
    if 'full_payment' in allowed_methods and full_safe:
        candidates.append({
            'method': 'full_payment',
            'is_safe': True,
            'cost': requested_amount,
            'plan': f"{start_date}:{format_amt(requested_amount)}",
            'option_id': 0,
            'spending_changes': spending_changes,
            'earliest_date_for_full_payment': start_date
        })

    # 2. wait
    if 'full_payment' in allowed_methods and earliest is not None and not full_safe:
        candidates.append({
            'method': 'wait',
            'is_safe': True,
            'cost': requested_amount,
            'plan': f"{earliest}:{format_amt(requested_amount)}",
            'option_id': 0,
            'spending_changes': spending_changes,
            'earliest_date_for_full_payment': earliest
        })

    # 3. partial_payment
    if allows_partial and 'partial_payment' in allowed_methods and 0 < safe_amt < requested_amount and earliest is not None:
        if earliest <= desired_date:
            rem_amt = round(requested_amount - safe_amt, 2)
            candidates.append({
                'method': 'partial_payment',
                'is_safe': True,
                'cost': requested_amount,
                'plan': f"{start_date}:{format_amt(safe_amt)}|{earliest}:{format_amt(rem_amt)}",
                'option_id': 0,
                'spending_changes': spending_changes,
                'earliest_date_for_full_payment': earliest
            })
        
    # 4. installments
    if 'installments' in allowed_methods and not options.empty:
        for _, opt in options.iterrows():
            method = opt['payment_method']
            if method == 'installments':
                num_payments = int(opt['number_of_payments'])
                days_between = int(opt['payment_frequency_days'])
                
                # Calculate start_date_offset from first_payment_date
                first_pay_dt = datetime.strptime(opt['first_payment_date'], '%Y-%m-%d')
                req_dt = datetime.strptime(start_date, '%Y-%m-%d')
                start_offset = (first_pay_dt - req_dt).days
                
                total = float(opt['total_payable_amount'])
                opt_id = opt['payment_option_id']
                
                try:
                    num_opt_id = int(str(opt_id).replace('payment_option_', ''))
                except:
                    num_opt_id = 999
                
                per_payment = total / num_payments
                plan_str = []
                plan_dict = {}
                current = first_pay_dt
                
                for i in range(num_payments):
                    d_str = current.strftime('%Y-%m-%d')
                    plan_str.append(f"{d_str}:{format_amt(per_payment)}")
                    plan_dict[d_str] = round(per_payment, 2)
                    current += timedelta(days=days_between)
                    
                plan_str_joined = "|".join(plan_str)
                
                _, is_safe = forecaster.forecast_balance(start_balance, start_date, daily_flows, min_balance, plan_dict)
                if is_safe:
                    candidates.append({
                        'method': method,
                        'is_safe': True,
                        'cost': total,
                        'plan': plan_str_joined,
                        'option_id': num_opt_id,
                        'spending_changes': spending_changes,
                        'earliest_date_for_full_payment': earliest if earliest else ""
                    })

    if not candidates:
        return None

    # Sort candidates using 6-level tie breaker
    def rank_key(c):
        comp_date = get_completion_date(c['plan'], start_date)
        # 1. Complete by desired_date (True > False -> 0, 1 for sort)
        completes_in_time = 0 if comp_date <= desired_date else 1
        
        # 2. No spending changes (True > False -> 0, 1)
        no_changes = 0 if c['spending_changes'] == "none" else 1
        
        # 3. Minimize total amount paid
        cost = c['cost']
        
        # 4. Start payment earlier
        start_d = get_start_date(c['plan'], start_date)
        
        # 5. Fewer payments
        num_pmt = get_num_payments(c['plan'])
        
        # 6. Lowest payment_option_id
        oid = c['option_id']
        
        return (completes_in_time, no_changes, cost, start_d, num_pmt, oid)
        
    candidates.sort(key=rank_key)
    return candidates[0]

def apply_greedy_spending_changes(events_df, start_balance, start_date, daily_flows, min_balance, requested_amount, forecaster):
    if events_df.empty:
        return "none", daily_flows

    flex = events_df[(events_df['is_flexible'] == True) | (events_df['is_flexible'] == 'true') | (events_df['is_flexible'] == 'True')]
    flex = flex[(flex['is_recurring'] == True) | (flex['is_recurring'] == 'true') | (flex['is_recurring'] == 'True')]
    if flex.empty:
        return "none", daily_flows

    flex = flex.copy()
    flex['abs_amount'] = flex['amount'].astype(float).abs()
    flex = flex.sort_values(by='abs_amount', ascending=False)
    
    stop_list = []
    current_flows = daily_flows.copy()
    
    for _, row in flex.head(3).iterrows():
        stop_list.append(f"stop:{row['event_id']}")
        # simplified: add back the positive equivalent across 90 days for this recurring expense
        # assuming it happens every 30 days
        event_dt = pd.to_datetime(row['event_date'])
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        for i in range(1, 6):
            next_dt = event_dt + timedelta(days=30*i)
            if next_dt >= start_dt:
                date_str = next_dt.strftime('%Y-%m-%d')
                current_flows[date_str] = current_flows.get(date_str, 0.0) + row['abs_amount']
                
    if not stop_list:
        return "none", daily_flows
        
    return "|".join(stop_list), current_flows
