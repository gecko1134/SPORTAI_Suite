import streamlit as st
from ai_modules.demand_forecasting import DemandForecaster
from ai_modules.scheduling_optimizer import optimize_schedule
from ai_modules.sponsorship_matcher import match_sponsors
from ai_modules.dynamic_contract_generator import generate_contract
from ai_modules.membership_churn import ChurnPredictor
from ai_modules.marketing_optimizer import optimize_campaign

st.sidebar.title('AI Optimizations')

if st.sidebar.button('Forecast Demand'):
    st.write('Demand Forecast:')
    # TODO: load booking_data.csv and call DemandForecaster.predict()

if st.sidebar.button('Optimize Schedule'):
    st.write('Optimized Schedule:')
    # TODO: load schedule_requests.csv, resources.json, call optimize_schedule()

if st.sidebar.button('Match Sponsors'):
    st.write('Sponsor Matches:')
    # TODO: load assets.csv and sponsors.csv, call match_sponsors()

if st.sidebar.button('Generate Dynamic Contract'):
    st.write('Contract Link:')
    # TODO: call generate_contract(template_id, data, api_key) and show URL

if st.sidebar.button('Predict Churn'):
    st.write('Churn Risk Scores:')
    # TODO: load member_features.csv, call ChurnPredictor.predict()

if st.sidebar.button('Optimize Campaign'):
    st.write('Campaign Result:')
    # TODO: load invites.csv, call optimize_campaign()

st.title('SportAI Suite with AI Modules')
st.write('Select an AI tool from the sidebar to get started.')
