import streamlit as st
import pandas as pd
import ast
import plotly.graph_objects as go
import numpy as np

# Configure the page
st.set_page_config(
    page_title="Buy or Wait? Premium UI",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for the Meta AI clone
st.markdown("""
<style>
    /* Global Background and Fonts */
    .stApp {
        background-color: #f9f9f9;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Hide top header and menu */
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Top Navigation Bar */
    .navbar {
        display: flex;
        align-items: center;
        padding: 10px 40px;
        background: white;
        border-bottom: 1px solid #eaeaea;
        margin-top: -60px;
        margin-bottom: 30px;
    }
    .navbar-brand {
        font-weight: 800;
        font-size: 1.2rem;
        margin-right: 30px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .navbar-brand span {
        background: black;
        color: white;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 0.8rem;
    }
    .navbar-links {
        display: flex;
        gap: 20px;
        color: #666;
        font-weight: 500;
        font-size: 0.95rem;
    }
    .navbar-links .active {
        color: black;
        background: #f0f0f0;
        padding: 6px 12px;
        border-radius: 20px;
    }
    
    /* Typography */
    .main-greeting {
        font-size: 2.8rem;
        font-weight: 800;
        color: #111;
        margin-bottom: 0px;
        padding-bottom: 0px;
    }
    .sub-greeting {
        font-size: 1.2rem;
        color: #555;
        margin-top: -10px;
        margin-bottom: 30px;
    }
    
    /* Cards */
    .white-card {
        background: white;
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        height: 100%;
        border: 1px solid #f0f0f0;
    }
    .dark-card {
        background: #111;
        color: white;
        border-radius: 20px;
        padding: 30px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        height: 100%;
        display: flex;
        flex-direction: column;
    }
    .dark-card-title {
        text-transform: uppercase;
        font-size: 0.75rem;
        letter-spacing: 1px;
        color: #999;
        margin-bottom: 10px;
    }
    .dark-card-verdict {
        font-size: 3.5rem;
        font-weight: 800;
        line-height: 1;
        margin-bottom: 5px;
        font-family: serif;
    }
    .dark-card-subtitle {
        color: #aaa;
        font-size: 1rem;
        margin-bottom: 20px;
    }
    .dark-card-box {
        background: #222;
        border-radius: 12px;
        padding: 15px;
        font-size: 0.9rem;
        color: #ddd;
        margin-bottom: 20px;
    }
    .dark-button {
        background: white;
        color: black;
        text-align: center;
        padding: 12px;
        border-radius: 25px;
        font-weight: bold;
        margin-top: auto;
        cursor: pointer;
    }
    
    /* Transaction List */
    .tx-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 0;
        border-bottom: 1px solid #f5f5f5;
    }
    .tx-left {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .tx-icon {
        width: 32px; height: 32px;
        background: #f5f5f5;
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 14px;
    }
    .tx-title { font-weight: 600; font-size: 0.95rem; color: #111; }
    .tx-sub { font-size: 0.8rem; color: #888; }
    .tx-amount { font-weight: 700; font-size: 0.95rem; }
    .tx-positive { color: #2ca02c; }
    
</style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    req_df = pd.read_csv('dataset/requests.csv')
    out_df = pd.read_csv('output.csv')
    prof_df = pd.read_csv('dataset/financial_profiles.csv')
    ev_df = pd.read_csv('dataset/financial_events.csv')
    
    df = pd.merge(req_df, out_df, on='request_id', how='left')
    df = pd.merge(df, prof_df, on='user_id', how='left')
    return df, ev_df

try:
    df, ev_df = load_data()
except Exception as e:
    st.error(f"Failed to load data. Details: {e}")
    st.stop()

# Build the Navbar
st.markdown("""
<div class="navbar">
    <div class="navbar-brand"><span>B</span> Buy or Wait? <small style="color:#888; font-weight:normal; font-size:0.7rem; border:1px solid #ccc; padding:2px 4px; border-radius:4px; margin-left:5px;">BETA</small></div>
    <div class="navbar-links">
        <div class="active">Dashboard</div>
        <div>Insights</div>
        <div>Spending</div>
        <div>Payments</div>
    </div>
    <div style="margin-left:auto; display:flex; gap:15px; align-items:center;">
        <span style="font-size:0.85rem; font-weight:500; color:#555;">🟢 Agent Live Forecast • 12ms</span>
        <div style="background:black; color:white; padding:6px 15px; border-radius:20px; font-size:0.85rem; font-weight:600;">+ New Plan</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Main Selector
user_list = df['user_id'].unique().tolist()
selected_user = st.selectbox("Select User Profile", user_list, label_visibility="collapsed")
user_row = df[df['user_id'] == selected_user].iloc[0]
req_amount = user_row['requested_amount']
balance = user_row['current_available_balance']
status = user_row['affordability_status']

# Greeting
st.markdown(f'<div class="main-greeting">Good morning, {selected_user}.</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-greeting">You\'re deciding on a purchase of <strong>${req_amount:,.2f}</strong>. We ran the numbers. <span style="float:right; font-size:0.8rem; color:#2ca02c;">● All accounts synced</span></div>', unsafe_allow_html=True)

# Layout Row 1
col1, col2, col3 = st.columns([2.5, 1, 1.2])

with col1:
    st.markdown('<div class="white-card">', unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.8rem; font-weight:700; color:#888; letter-spacing:1px; margin-bottom:5px;">90-DAY BALANCE FORECAST <span style="background:#e0f2f1; color:#00796b; padding:2px 6px; border-radius:4px; font-size:0.7rem; margin-left:8px;">AGENT</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div style="font-size:2.2rem; font-weight:800; margin-bottom:0px;">${balance:,.0f} <span style="font-size:0.9rem; color:#2ca02c; background:#e8f5e9; padding:4px 8px; border-radius:12px; font-weight:600; vertical-align:middle;">+2.4% vs last forecast</span></div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.9rem; color:#666; margin-bottom:20px;">After rent, subscriptions, and this purchase on split plan</div>', unsafe_allow_html=True)
    
    # Mocking a realistic balance drop graph
    days = np.arange(90)
    base_trend = balance - (days * 5) + (np.sin(days / 5) * 200)
    # create a dip around day 30
    dip = np.where((days > 25) & (days < 40), -req_amount * 0.8, 0)
    dip = dip + np.where((days >= 40), -req_amount * 0.2, 0)
    y_vals = base_trend + dip
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=days, y=y_vals, fill='tozeroy', mode='lines', line=dict(color='#333', width=2), fillcolor='rgba(0,0,0,0.05)'))
    
    # Highlight the dip area
    fig.add_vrect(x0=25, x1=40, fillcolor="red", opacity=0.05, line_width=0)
    
    fig.update_layout(
        margin=dict(l=0, r=0, t=10, b=0),
        height=220,
        xaxis=dict(showgrid=False, showticklabels=True, tickvals=[0, 30, 60, 90], ticktext=["Today", "30 days", "60 days", "90 days"], linecolor="#eee"),
        yaxis=dict(showgrid=False, showticklabels=False),
        plot_bgcolor='white', paper_bgcolor='white'
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    lowest = np.min(y_vals)
    st.markdown(f'<div style="background:#fff8e1; border:1px solid #ffe082; padding:10px; border-radius:8px; font-size:0.85rem; color:#8d6e63; margin-top:10px;">⚠️ Lowest point <strong>${lowest:,.0f}</strong> on Day 38 — rent week. Split plan avoids this dip.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="white-card">', unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.8rem; font-weight:700; color:#888; letter-spacing:1px; margin-bottom:20px; text-transform:uppercase;">Affordability Score</div>', unsafe_allow_html=True)
    
    score = 84 if 'affordable' in status and 'not' not in status else 32
    if status == 'affordable_later': score = 65
    
    color = "#111" if score > 50 else "#d62728"
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        number = {'font': {'size': 50, 'color': '#111', 'family': 'sans-serif', 'weight': 'bold'}},
        gauge = {
            'axis': {'range': [None, 100], 'visible': False},
            'bar': {'color': color, 'thickness': 0.8},
            'bgcolor': "#f0f0f0",
            'borderwidth': 0,
            'shape': "angular"
        }
    ))
    fig_gauge.update_layout(height=180, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor='white', font={'family': "Arial"})
    
    # Custom HTML overlay for the gauge subtitle "Strong"
    st.plotly_chart(fig_gauge, use_container_width=True, config={'displayModeBar': False})
    
    label = "Strong" if score > 70 else ("Moderate" if score > 50 else "Weak")
    st.markdown(f'<div style="text-align:center; font-weight:800; background:{color}; color:white; width:fit-content; margin: -40px auto 30px auto; padding:4px 12px; border-radius:12px; font-size:0.8rem; position:relative; z-index:10;">{label}</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="font-size:0.85rem; margin-top:20px;">
        <div style="display:flex; justify-content:space-between; margin-bottom:5px;"><span>Cash flow</span> <span style="font-weight:600;">Good • 78</span></div>
        <div style="height:4px; background:#eee; border-radius:2px; margin-bottom:15px;"><div style="height:100%; width:78%; background:#111; border-radius:2px;"></div></div>
        <div style="display:flex; justify-content:space-between; margin-bottom:5px;"><span>Buffer</span> <span style="font-weight:600;">Low • 42</span></div>
        <div style="height:4px; background:#eee; border-radius:2px;"><div style="height:100%; width:42%; background:#888; border-radius:2px;"></div></div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    verdict_map = {
        'affordable_now': ('Buy', 'Now'),
        'affordable_with_plan': ('Split', 'Plan'),
        'affordable_later': ('Wait', 'Few weeks'),
        'not_affordable': ('Reject', 'Unsafe')
    }
    v_title, v_sub = verdict_map.get(status, ('Wait', '1.8 weeks'))
    
    st.markdown(f"""
    <div class="dark-card">
        <div class="dark-card-title">Agent Recommends</div>
        <div class="dark-card-verdict">{v_title}</div>
        <div class="dark-card-subtitle">{v_sub}</div>
        
        <div class="dark-card-box">
            Paying now drops you to <strong>${lowest:,.0f}</strong> on rent week. Waiting keeps you above $3.2k and earns $23 in interest.
            <div style="margin-top:10px;">
                <span style="background:rgba(255,255,255,0.2); padding:4px 8px; border-radius:4px; font-size:0.75rem;">+23% safer</span>
                <span style="background:rgba(255,255,255,0.1); padding:4px 8px; border-radius:4px; font-size:0.75rem; margin-left:5px;">Auto-split eligible</span>
            </div>
        </div>
        
        <div class="dark-button">Set reminder for May 3</div>
        <div style="text-align:center; color:#666; font-size:0.75rem; margin-top:15px;">You can still buy earlier if price drops</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Layout Row 2
col4, col5, col6 = st.columns([1.5, 1, 1.5])

with col4:
    st.markdown('<div class="white-card">', unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.9rem; font-weight:700; margin-bottom:20px;">Payment Plan Options <span style="float:right; font-weight:normal; font-size:0.8rem; color:#888;">Apple Store • 0% APR</span></div>', unsafe_allow_html=True)
    
    # Render two plan cards
    rec_method = user_row['recommended_payment_method']
    st.markdown(f"""
    <div style="display:flex; gap:15px; margin-bottom:20px;">
        <div style="flex:1; border:1px solid #eee; border-radius:12px; padding:20px; background:#fafafa;">
            <div style="font-size:0.75rem; font-weight:700; color:#888; margin-bottom:10px;">PAY NOW</div>
            <div style="font-size:1.8rem; font-weight:800; margin-bottom:5px;">${req_amount:,.0f}</div>
            <div style="font-size:0.8rem; color:#666;">One-time • Today</div>
            <div style="margin-top:20px; font-size:0.75rem; color:#888;">Balance dips to ${lowest:,.0f}</div>
        </div>
        <div style="flex:1; border:2px solid #111; border-radius:12px; padding:20px; position:relative;">
            <div style="position:absolute; top:-10px; right:10px; background:#111; color:white; font-size:0.6rem; font-weight:800; padding:3px 8px; border-radius:10px; letter-spacing:1px;">RECOMMENDED</div>
            <div style="font-size:0.75rem; font-weight:700; color:#555; margin-bottom:10px;">{rec_method.upper()}</div>
            <div style="font-size:1.8rem; font-weight:800; margin-bottom:5px;">${req_amount/3:,.0f} <span style="font-size:1rem; font-weight:normal; color:#888;">/mo</span></div>
            <div style="font-size:0.8rem; color:#666;">No fees • 0% APR</div>
            <div style="margin-top:20px; font-size:0.75rem; color:#00796b; font-weight:600; background:#e0f2f1; padding:4px 8px; border-radius:4px; display:inline-block;">Keeps buffer above $3.2k</div>
        </div>
    </div>
    
    <div style="border:1px solid #eee; border-radius:12px; padding:15px; display:flex; justify-content:space-between; align-items:center; background:#fafafa;">
        <div style="display:flex; align-items:center; gap:15px;">
            <div style="width:30px; height:30px; background:white; border:1px solid #ddd; border-radius:6px; display:flex; align-items:center; justify-content:center;">💳</div>
            <div>
                <div style="font-weight:600; font-size:0.9rem;">Apple Card Monthly Installments</div>
                <div style="font-size:0.75rem; color:#888;">3% Daily Cash back • $27 back</div>
            </div>
        </div>
        <div style="font-size:0.8rem; color:#888;">Learn →</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col5:
    st.markdown('<div class="white-card">', unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.9rem; font-weight:700; margin-bottom:20px;">Cash & Spending</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="margin-bottom:15px;">
        <div style="display:flex; justify-content:space-between; font-size:0.85rem; color:#555; margin-bottom:5px;"><span>Income • Dec</span> <span style="font-weight:700; color:#111;">$6,800</span></div>
        <div style="height:6px; background:#111; border-radius:3px; width:100%;"></div>
    </div>
    <div style="margin-bottom:30px;">
        <div style="display:flex; justify-content:space-between; font-size:0.85rem; color:#555; margin-bottom:5px;"><span>Expenses</span> <span style="font-weight:700; color:#111;">$4,120</span></div>
        <div style="height:6px; background:#eee; border-radius:3px; width:100%;"><div style="height:100%; width:60%; background:#888; border-radius:3px;"></div></div>
    </div>
    
    <div style="background:#111; color:white; padding:20px; border-radius:16px; margin-bottom:20px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
            <span style="font-size:0.7rem; font-weight:700; color:#888; letter-spacing:1px;">REMAINING</span>
            <span style="background:rgba(255,255,255,0.15); padding:2px 8px; border-radius:10px; font-size:0.7rem; font-weight:600;">68% saved</span>
        </div>
        <div style="font-size:2rem; font-weight:800; margin-bottom:10px;">$2,680</div>
        <div style="font-size:0.8rem; color:#aaa; line-height:1.4;">After rent & essentials. +$430 vs last month.</div>
    </div>
    
    <div style="display:flex; justify-content:space-between; text-align:center;">
        <div><div style="font-size:0.7rem; font-weight:700; color:#888; letter-spacing:1px; margin-bottom:5px;">RENT</div><div style="font-weight:700; font-size:0.9rem;">$1,850</div></div>
        <div><div style="font-size:0.7rem; font-weight:700; color:#888; letter-spacing:1px; margin-bottom:5px;">FOOD</div><div style="font-weight:700; font-size:0.9rem;">$412</div></div>
        <div><div style="font-size:0.7rem; font-weight:700; color:#888; letter-spacing:1px; margin-bottom:5px;">FUN</div><div style="font-weight:700; font-size:0.9rem;">$298</div></div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col6:
    st.markdown('<div class="white-card">', unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.9rem; font-weight:700; margin-bottom:20px;">Recent Transactions <span style="float:right; font-weight:normal; font-size:0.8rem; color:#888;">View all →</span></div>', unsafe_allow_html=True)
    
    # Render some mock transactions to match the UI perfectly
    tx_html = """
    <div class="tx-item">
        <div class="tx-left">
            <div class="tx-icon">◑</div>
            <div>
                <div class="tx-title">Figma Annual</div>
                <div class="tx-sub">Software • Today, 9:42 AM</div>
            </div>
        </div>
        <div class="tx-amount">$144</div>
    </div>
    <div class="tx-item">
        <div class="tx-left">
            <div class="tx-icon">↗</div>
            <div>
                <div class="tx-title">Chase • Checking</div>
                <div class="tx-sub">Transfer in • Yesterday</div>
            </div>
        </div>
        <div class="tx-amount tx-positive">+$2,400</div>
    </div>
    <div class="tx-item">
        <div class="tx-left">
            <div class="tx-icon">◑</div>
            <div>
                <div class="tx-title">Whole Foods</div>
                <div class="tx-sub">Groceries • Dec 11</div>
            </div>
        </div>
        <div class="tx-amount">$86.32</div>
    </div>
    <div class="tx-item">
        <div class="tx-left">
            <div class="tx-icon">✈</div>
            <div>
                <div class="tx-title">United • SFO → JFK</div>
                <div class="tx-sub">Travel • Dec 10</div>
            </div>
        </div>
        <div class="tx-amount">$412</div>
    </div>
    <div class="tx-item" style="border-bottom:none;">
        <div class="tx-left">
            <div class="tx-icon">↓</div>
            <div>
                <div class="tx-title">Stripe Payout</div>
                <div class="tx-sub">Income • Dec 09</div>
            </div>
        </div>
        <div class="tx-amount tx-positive">+$1,240</div>
    </div>
    
    <div style="margin-top:15px; border:1px dashed #ccc; padding:15px; border-radius:12px; font-size:0.85rem; color:#555; display:flex; align-items:center; gap:10px;">
        <div style="background:black; color:white; width:20px; height:20px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:0.6rem;">/</div>
        <strong>2 upcoming bills</strong> • $324 due in 4 days
    </div>
    """
    st.markdown(tx_html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("""
<div style="display:flex; justify-content:space-between; margin-top:20px; font-size:0.75rem; color:#aaa;">
    <div style="display:flex; gap:15px; align-items:center;">
        <span style="color:#2ca02c;">● Data updated 2 min ago</span>
        <span><strong style="color:white; background:#0052cc; padding:2px 6px; border-radius:50%; margin-right:5px;">C</strong> Connected to Chase • 2 accounts</span>
    </div>
    <div>Agent Forecast • Confidence 94% • Privacy • Encrypted end-to-end</div>
</div>
""", unsafe_allow_html=True)
