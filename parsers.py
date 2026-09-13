import json
import os
import pandas as pd
import numpy as np
from datetime import datetime
from vlm_extractor import extract_amount_from_image

def load_exchange_rates(exchange_rates_path: str):
    if not os.path.exists(exchange_rates_path):
        return {}
    df = pd.read_csv(exchange_rates_path)
    rates = {}
    for _, row in df.iterrows():
        rates[(row['rate_date'], row['from_currency'], row['to_currency'])] = float(row['rate'])
    return rates

def convert_currency(amount: float, from_curr: str, to_curr: str, date: str, rates: dict) -> float:
    if from_curr == to_curr or pd.isna(from_curr):
        return amount
    # direct
    if (date, from_curr, to_curr) in rates:
        return amount * rates[(date, from_curr, to_curr)]
    # reverse direct
    if (date, to_curr, from_curr) in rates:
        return amount / rates[(date, to_curr, from_curr)]
    # USD bridge
    rate_to_usd = 1.0
    if from_curr != 'USD':
        if (date, from_curr, 'USD') in rates:
            rate_to_usd = rates[(date, from_curr, 'USD')]
        elif (date, 'USD', from_curr) in rates:
            rate_to_usd = 1.0 / rates[(date, 'USD', from_curr)]
            
    rate_from_usd = 1.0
    if to_curr != 'USD':
        if (date, 'USD', to_curr) in rates:
            rate_from_usd = rates[(date, 'USD', to_curr)]
        elif (date, to_curr, 'USD') in rates:
            rate_from_usd = 1.0 / rates[(date, to_curr, 'USD')]
            
    return amount * rate_to_usd * rate_from_usd

def filter_events(user_events_df: pd.DataFrame, request_date: str, images_df: pd.DataFrame, media_dir: str, home_currency: str, rates: dict):
    if user_events_df.empty:
        return user_events_df

    df = user_events_df.copy()
    df['event_date'] = pd.to_datetime(df['event_date'])
    df = df.sort_values(by='event_date')

    # Deduplicate via linked_event_id
    linked_ids = set(df['linked_event_id'].dropna().unique())
    df = df[~df['event_id'].isin(linked_ids)]

    # Filter status
    df = df[~df['status'].isin(['failed', 'cancelled', 'void'])]

    # Filter pending credit
    if 'is_pending' in df.columns:
        df = df[~(((df['is_pending'] == True) | (df['is_pending'] == 'true') | (df['is_pending'] == 'True')) & (df['direction'] == 'credit'))]

    # Filter unrealized investments
    df = df[~((df['event_type'] == 'investment') & (df['status'] != 'settled'))]

    # Convert dates back to string
    df['event_date'] = df['event_date'].dt.strftime('%Y-%m-%d')

    # Handle blank amount and currency conversion
    for idx, row in df.iterrows():
        amt = row['amount']
        if pd.isna(amt) or amt == '' or amt == 0:
            if images_df is not None and not images_df.empty:
                img_row = images_df[images_df['related_event_id'] == row['event_id']]
                if not img_row.empty:
                    img_id = img_row.iloc[0]['image_id']
                    img_path = os.path.join(media_dir, f"{img_id}.png")
                    amt = extract_amount_from_image(img_path, img_id)
                    if amt is not None:
                        df.at[idx, 'amount'] = amt
        
        # Currency conversion
        if not pd.isna(amt):
            evt_curr = row['currency'] if 'currency' in df.columns and not pd.isna(row['currency']) else home_currency
            evt_date = row['event_date']
            # Fallback to request_date if evt_date not in rates
            date_to_use = evt_date if any(k[0] == evt_date for k in rates.keys()) else request_date
            converted_amt = convert_currency(float(amt), evt_curr, home_currency, date_to_use, rates)
            df.at[idx, 'amount'] = converted_amt

    return df

def apply_messages_to_events(events_df: pd.DataFrame, msg_results: dict):
    if events_df.empty or not msg_results:
        return events_df
    df = events_df.copy()
    to_drop = []
    for msg_id, info in msg_results.items():
        evt_id = info.get('related_event_id')
        cls = info.get('classification')
        if not evt_id or evt_id not in df['event_id'].values:
            continue
        if cls == 'cancel':
            to_drop.append(evt_id)
        elif cls == 'amend_amount' and info.get('new_amount') is not None:
            df.loc[df['event_id'] == evt_id, 'amount'] = float(info['new_amount'])
        elif cls == 'delay_date' and info.get('new_date') is not None:
            df.loc[df['event_id'] == evt_id, 'event_date'] = str(info['new_date'])
            
    if to_drop:
        df = df[~df['event_id'].isin(to_drop)]
    return df
