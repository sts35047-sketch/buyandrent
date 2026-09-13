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

# Custom CSS for the interactive Meta AI clone
st.markdown("""
<style>
    .stApp {
        background-color: #f9f9f9;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .navbar {
        display: flex;
        align-items: center;
        padding: 10px 40px;
        background: white;
        border-bottom: 1px solid #eaeaea;
        margin-top: -60px;
        margin-bottom: 10px;
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
    
    /* Typography */
    .main-greeting { font-size: 2.8rem; font-weight: 800; color: #111; margin-bottom: 0px; padding-bottom: 0px; }
    .sub-greeting { font-size: 1.2rem; color: #555; margin-top: -10px; margin-bottom: 20px; }
    
    /* Cards */
    .white-card {
        background: white; border-radius: 20px; padding: 25px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03); height: 100%; border: 1px solid #f0f0f0;
    }
    .dark-card {
        background: #111; color: white; border-radius: 20px; padding: 25px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1); height: 100%; display: flex; flex-direction: column;
    }
    
    /* Streamlit Tabs overriding to look like nav */
    .stTabs [data-baseweb="tab-list"] {
        gap: 30px;
        border-bottom: none;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px; white-space: pre-wrap; background-color: transparent;
        border-radius: 4px; padding-top: 10px; padding-bottom: 10px; font-weight: 600; color: #666;
    }
    .stTabs [aria-selected="true"] {
        color: black !important; background: #f0f0f0 !important; border-radius: 20px !important; padding: 10px 15px !important;
    }
    
    /* Adjust buttons to look like links or native buttons */
    .stButton>button {
        border-radius: 25px; font-weight: 600;
    }
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
    st.error(f"Failed to load data: {e}")
    st.stop()

# Build the Navbar Top
st.markdown("""
<div class="navbar">
    <div class="navbar-brand"><span>B</span> Buy or Wait? <small style="color:#888; font-weight:normal; font-size:0.7rem; border:1px solid #ccc; padding:2px 4px; border-radius:4px; margin-left:5px;">BETA</small></div>
    <div style="margin-left:auto; display:flex; gap:15px; align-items:center;">
        <span style="font-size:0.85rem; font-weight:500; color:#555;">🟢 Agent Live Forecast • 12ms</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Toolbar
col_user, col_plan = st.columns([5, 1])
with col_user:
    user_list = df['user_id'].unique().tolist()
    selected_user = st.selectbox("Select User Profile", user_list, label_visibility="collapsed")
with col_plan:
    if st.button("➕ New Plan", use_container_width=True):
        st.toast("Redirecting to New Plan builder...")

user_row = df[df['user_id'] == selected_user].iloc[0]
req_amount = user_row['requested_amount']
balance = user_row['current_available_balance']
status = user_row['affordability_status']

# Greeting
st.markdown(f'<div class="main-greeting">Good morning, {selected_user}.</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-greeting">You\'re deciding on a purchase of <strong>${req_amount:,.2f}</strong>. We ran the numbers. <span style="float:right; font-size:0.8rem; color:#2ca02c;">● All accounts synced</span></div>', unsafe_allow_html=True)

# TABS for interactive navigation
tab_dash, tab_ins, tab_spend, tab_pay = st.tabs(["Dashboard", "Insights", "Spending", "Payments"])

with tab_dash:
    # Layout Row 1
    col1, col2, col3 = st.columns([2.5, 1, 1.2])

    with col1:
        st.markdown('<div class="white-card">', unsafe_allow_html=True)
        st.markdown('<div style="font-size:0.8rem; font-weight:700; color:#888; letter-spacing:1px; margin-bottom:5px;">90-DAY BALANCE FORECAST <span style="background:#e0f2f1; color:#00796b; padding:2px 6px; border-radius:4px; font-size:0.7rem; margin-left:8px;">AGENT</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size:2.2rem; font-weight:800; margin-bottom:0px;">${balance:,.0f} <span style="font-size:0.9rem; color:#2ca02c; background:#e8f5e9; padding:4px 8px; border-radius:12px; font-weight:600; vertical-align:middle;">+2.4% vs last forecast</span></div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size:0.9rem; color:#666; margin-bottom:10px;">After rent, subscriptions, and this purchase on split plan</div>', unsafe_allow_html=True)
        
        # Mock graph
        days = np.arange(90)
        base_trend = balance - (days * 5) + (np.sin(days / 5) * 200)
        dip = np.where((days > 25) & (days < 40), -req_amount * 0.8, 0) + np.where((days >= 40), -req_amount * 0.2, 0)
        y_vals = base_trend + dip
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=days, y=y_vals, fill='tozeroy', mode='lines', line=dict(color='#333', width=2), fillcolor='rgba(0,0,0,0.05)'))
        fig.add_vrect(x0=25, x1=40, fillcolor="red", opacity=0.05, line_width=0)
        fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=180, xaxis=dict(showgrid=False, showticklabels=True, tickvals=[0, 30, 60, 90], ticktext=["Today", "30 days", "60 days", "90 days"], linecolor="#eee"), yaxis=dict(showgrid=False, showticklabels=False), plot_bgcolor='white', paper_bgcolor='white')
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        lowest = np.min(y_vals)
        st.markdown(f'<div style="background:#fff8e1; border:1px solid #ffe082; padding:10px; border-radius:8px; font-size:0.85rem; color:#8d6e63;">⚠️ Lowest point <strong>${lowest:,.0f}</strong> on Day 38 — rent week. Split plan avoids this dip.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="white-card">', unsafe_allow_html=True)
        st.markdown('<div style="font-size:0.8rem; font-weight:700; color:#888; letter-spacing:1px; margin-bottom:20px; text-transform:uppercase;">Affordability Score</div>', unsafe_allow_html=True)
        score = 84 if 'affordable' in status and 'not' not in status else 32
        if status == 'affordable_later': score = 65
        color = "#111" if score > 50 else "#d62728"
        fig_gauge = go.Figure(go.Indicator(mode = "gauge+number", value = score, number = {'font': {'size': 50, 'color': '#111', 'family': 'sans-serif', 'weight': 'bold'}}, gauge = {'axis': {'range': [None, 100], 'visible': False}, 'bar': {'color': color, 'thickness': 0.8}, 'bgcolor': "#f0f0f0", 'borderwidth': 0, 'shape': "angular"}))
        fig_gauge.update_layout(height=160, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor='white')
        st.plotly_chart(fig_gauge, use_container_width=True, config={'displayModeBar': False})
        
        label = "Strong" if score > 70 else ("Moderate" if score > 50 else "Weak")
        st.markdown(f'<div style="text-align:center; font-weight:800; background:{color}; color:white; width:fit-content; margin: -40px auto 30px auto; padding:4px 12px; border-radius:12px; font-size:0.8rem; position:relative; z-index:10;">{label}</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size:0.85rem; margin-top:10px;"><div style="display:flex; justify-content:space-between; margin-bottom:5px;"><span>Cash flow</span> <span style="font-weight:600;">Good • 78</span></div><div style="height:4px; background:#eee; border-radius:2px; margin-bottom:15px;"><div style="height:100%; width:78%; background:#111; border-radius:2px;"></div></div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        verdict_map = {'affordable_now': ('Buy', 'Now'), 'affordable_with_plan': ('Split', 'Plan'), 'affordable_later': ('Wait', 'Few weeks'), 'not_affordable': ('Reject', 'Unsafe')}
        v_title, v_sub = verdict_map.get(status, ('Wait', '1.8 weeks'))
        
        st.markdown(f"""
        <div class="dark-card">
            <div style="text-transform: uppercase; font-size: 0.75rem; letter-spacing: 1px; color: #999; margin-bottom: 10px;">Agent Recommends</div>
            <div style="font-size: 3.5rem; font-weight: 800; line-height: 1; margin-bottom: 5px; font-family: serif;">{v_title}</div>
            <div style="color: #aaa; font-size: 1rem; margin-bottom: 10px;">{v_sub}</div>
            <div style="background: #222; border-radius: 12px; padding: 15px; font-size: 0.85rem; color: #ddd; margin-bottom: 15px;">
                Paying now drops you to <strong>${lowest:,.0f}</strong> on rent week. Waiting keeps you above $3.2k and earns $23 in interest.
            </div>
        </div>
        """, unsafe_allow_html=True)
        # Interactive Button injected into dark card flow via container hack
        if st.button("🔔 Set reminder for May 3", use_container_width=True):
            st.toast("✅ Reminder set for May 3 successfully!")

    st.markdown("<br>", unsafe_allow_html=True)

    # Layout Row 2
    col4, col5, col6 = st.columns([1.5, 1, 1.5])

    with col4:
        st.markdown('<div class="white-card">', unsafe_allow_html=True)
        st.markdown('<div style="font-size:0.9rem; font-weight:700; margin-bottom:20px;">Payment Plan Options <span style="float:right; font-weight:normal; font-size:0.8rem; color:#888;">Apple Store • 0% APR</span></div>', unsafe_allow_html=True)
        
        rec_method = user_row['recommended_payment_method']
        st.markdown(f"""
        <div style="display:flex; gap:15px; margin-bottom:20px;">
            <div style="flex:1; border:1px solid #eee; border-radius:12px; padding:20px; background:#fafafa;">
                <div style="font-size:0.75rem; font-weight:700; color:#888; margin-bottom:10px;">PAY NOW</div>
                <div style="font-size:1.8rem; font-weight:800; margin-bottom:5px;">${req_amount:,.0f}</div>
                <div style="font-size:0.8rem; color:#666;">One-time • Today</div>
            </div>
            <div style="flex:1; border:2px solid #111; border-radius:12px; padding:20px; position:relative;">
                <div style="position:absolute; top:-10px; right:10px; background:#111; color:white; font-size:0.6rem; font-weight:800; padding:3px 8px; border-radius:10px;">RECOMMENDED</div>
                <div style="font-size:0.75rem; font-weight:700; color:#555; margin-bottom:10px;">{rec_method.upper()}</div>
                <div style="font-size:1.8rem; font-weight:800; margin-bottom:5px;">${req_amount/3:,.0f} <span style="font-size:1rem; font-weight:normal; color:#888;">/mo</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("💳 Apple Card Monthly Installments - Learn More"):
            st.info("Apple Card offers 3% Daily Cash back on this purchase.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col5:
        st.markdown('<div class="white-card">', unsafe_allow_html=True)
        st.markdown('<div style="font-size:0.9rem; font-weight:700; margin-bottom:20px;">Cash & Spending</div>', unsafe_allow_html=True)
        st.markdown("""
        <div style="background:#111; color:white; padding:20px; border-radius:16px; margin-bottom:20px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;"><span style="font-size:0.7rem; font-weight:700; color:#888; letter-spacing:1px;">REMAINING</span></div>
            <div style="font-size:2rem; font-weight:800; margin-bottom:10px;">$2,680</div>
            <div style="font-size:0.8rem; color:#aaa; line-height:1.4;">After rent & essentials.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("📊 View Budget Breakdown"):
            st.session_state['active_tab'] = "Spending"
            st.toast("Navigate to Spending Tab for full breakdown.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col6:
        st.markdown('<div class="white-card">', unsafe_allow_html=True)
        st.markdown('<div style="font-size:0.9rem; font-weight:700; margin-bottom:20px;">Recent Transactions</div>', unsafe_allow_html=True)
        
        # Real transactions from event DB for this user if available, else mock
        user_txs = ev_df[ev_df['user_id'] == selected_user].head(3)
        if len(user_txs) > 0:
            for _, tx in user_txs.iterrows():
                color = "green" if tx['amount'] > 0 else "black"
                st.markdown(f"**{tx['type'].capitalize()}** • {tx['event_date']} <span style='float:right; color:{color}; font-weight:bold;'>${tx['amount']:,.2f}</span>", unsafe_allow_html=True)
                st.markdown("<hr style='margin:10px 0px;'>", unsafe_allow_html=True)
        else:
            st.markdown("**No recent transactions.**")
            
        if st.button("📋 View all Transactions", use_container_width=True):
            st.toast(f"Loaded {len(ev_df[ev_df['user_id'] == selected_user])} transactions.")
        st.markdown('</div>', unsafe_allow_html=True)

with tab_ins:
    st.header("🧠 Agent Insights")
    st.markdown("Detailed LLM rationale behind this decision:")
    st.info(user_row['explanation'])
    st.warning("Spending Changes Required:")
    st.json(user_row['required_spending_changes'])

with tab_spend:
    st.header("💸 Spending Breakdown")
    st.markdown(f"**Priorities:** {user_row['financial_priorities']}")
    st.markdown(f"**Protected Categories:** {user_row['expense_categories_to_protect']}")
    st.markdown(f"**Willing to Reduce:** {user_row['expense_categories_user_is_willing_to_reduce']}")
    
with tab_pay:
    st.header("💳 Payment Method Alternatives")
    st.markdown(f"**Considered Methods:** {user_row['payment_methods_user_will_consider']}")
    schedule_str = user_row['payment_plan_schedule']
    if pd.notna(schedule_str) and schedule_str not in ('{}', ''):
        try:
            schedule = ast.literal_eval(schedule_str)
            st.table(pd.DataFrame(list(schedule.items()), columns=['Date', 'Installment Amount']))
        except:
            st.code(schedule_str)
    else:
        st.write("No specific installment plan schedule generated.")
