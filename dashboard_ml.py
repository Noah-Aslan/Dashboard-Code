import os
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import tensorflow as tf
import keras
from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout

st.set_page_config(
    page_title="Workforce ML — Heart Failure",
    layout="wide"
)
Dataset = 'Heart_Failure_Patient_Data_12_Months_20_Patients.xlsx'

@st.cache_data
def load_data():
    df_person   = pd.read_excel(Dataset, sheet_name='PERSON_MONTH_DATA')
    df_activity = pd.read_excel(Dataset, sheet_name='FCT_ACTIVITY_DATA')
    df_activity['ACTIVITY_MONTH'] = pd.to_datetime(df_activity['ACTIVITY_MONTH'])
    df_person['ANALYSIS_MONTH']   = pd.to_datetime(df_person['ANALYSIS_MONTH'])
    return df_person, df_activity

df_person, df_activity = load_data()

st.header("Workforce Planning & Predictions")
st.caption("Based on Jan 2024 – Dec 2024 | 20 heart failure patients | All services")


workforce = df_activity.groupby('ACTIVITY_MONTH').agg(
    GP_Encounters = ('GP_ENCOUNTERS', 'sum'),
    CC_Encounters = ('CC_ENCOUNTERS', 'sum'),
    IP_Encounters = ('IP_ENCOUNTERS', 'sum'),
    AE_Encounters = ('AE_ENCOUNTERS', 'sum'),
    OP_Encounters = ('OP_ENCOUNTERS', 'sum'),
    MH_Encounters = ('MH_ENCOUNTERS', 'sum'),
    GP_Hours      = ('GP_DURATION',   lambda x: x.sum() / 60),
    CC_Hours      = ('CC_DURATION',   lambda x: x.sum() / 60),
    IP_Hours      = ('IP_DURATION',   lambda x: x.sum() / 60),
    AE_Hours      = ('AE_DURATION',   lambda x: x.sum() / 60),
    OP_Hours      = ('OP_DURATION',   lambda x: x.sum() / 60),
    Total_Cost    = ('TOTAL_COST',    'sum'),
).reset_index()

workforce['Total_Hours'] = (
    workforce['GP_Hours'] + workforce['CC_Hours'] +
    workforce['IP_Hours'] + workforce['AE_Hours'] +
    workforce['OP_Hours']
)
workforce['Total_Encounters'] = (
    workforce['GP_Encounters'] + workforce['CC_Encounters'] +
    workforce['IP_Encounters'] + workforce['AE_Encounters'] +
    workforce['OP_Encounters'] + workforce['MH_Encounters']
)

st.subheader("Total workforce utilised — 2024")
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("Total encounters",     f"{int(workforce['Total_Encounters'].sum()):,}")
with col2:
    st.metric("Total staff hours",    f"{workforce['Total_Hours'].sum():,.0f} hrs")
with col3:
    st.metric("GP hours",             f"{workforce['GP_Hours'].sum():,.0f} hrs")
with col4:
    st.metric("Community care hours", f"{workforce['CC_Hours'].sum():,.0f} hrs")
with col5:
    st.metric("Total cost",           f"£{workforce['Total_Cost'].sum():,.0f}")

st.markdown("---")


st.subheader("Monthly encounters across all services")

fig_wf1 = go.Figure()
service_map = {
    'GP_Encounters': ('#3498DB', 'GP'),
    'CC_Encounters': ('#9B59B6', 'Community Care'),
    'OP_Encounters': ('#2ECC71', 'Outpatients'),
    'IP_Encounters': ('#E74C3C', 'Inpatients'),
    'AE_Encounters': ('#F39C12', 'A&E'),
    'MH_Encounters': ('#1ABC9C', 'Mental Health'),
}
for col, (colour, label) in service_map.items():
    fig_wf1.add_trace(go.Scatter(
        x=workforce['ACTIVITY_MONTH'], y=workforce[col],
        name=label, mode='lines', stackgroup='one',
        line=dict(color=colour, width=0.5),
    ))
fig_wf1.update_layout(
    title='Total workforce demand by service type (Jan–Dec 2024)',
    xaxis_title='Month', yaxis_title='Number of encounters',
    hovermode='x unified', height=420
)
st.plotly_chart(fig_wf1, use_container_width=True, key="fig_wf1")

# Stacked bar chart — staff hours by service per month
st.subheader("Staff hours utilised per month")

fig_wf2 = go.Figure()
hours_map = {
    'GP_Hours': ('#3498DB', 'GP hours'),
    'CC_Hours': ('#9B59B6', 'Community care hours'),
    'IP_Hours': ('#E74C3C', 'Inpatient hours'),
    'AE_Hours': ('#F39C12', 'A&E hours'),
    'OP_Hours': ('#2ECC71', 'Outpatient hours'),
}
for col, (colour, label) in hours_map.items():
    fig_wf2.add_trace(go.Bar(
        x=workforce['ACTIVITY_MONTH'], y=workforce[col],
        name=label, marker_color=colour
    ))
fig_wf2.update_layout(
    barmode='stack',
    title='Staff hours by service (Jan–Dec 2024)',
    xaxis_title='Month', yaxis_title='Hours',
    hovermode='x unified', height=420
)
st.plotly_chart(fig_wf2, use_container_width=True, key="fig_wf2")


st.markdown("---")
st.subheader("12-month demand forecast — next year (2025)")
st.caption("Uses Facebook Prophet: handles seasonality automatically on short time-series")

try:
    from prophet import Prophet

    forecast_target = st.selectbox(
        "Select service to forecast",
        options=['GP_Encounters', 'CC_Encounters', 'IP_Encounters',
                 'AE_Encounters', 'OP_Encounters'],
        format_func=lambda x: x.replace('_', ' ').replace('Encounters', '').strip()
    )

   
    prophet_df = workforce[['ACTIVITY_MONTH', forecast_target]].rename(
        columns={'ACTIVITY_MONTH': 'ds', forecast_target: 'y'}
    )


    m = Prophet(
        yearly_seasonality=False,
        weekly_seasonality=False,
        daily_seasonality=False,
        changepoint_prior_scale=0.1,
        interval_width=0.80
    )
    m.fit(prophet_df)

    future   = m.make_future_dataframe(periods=12, freq='MS')
    forecast = m.predict(future)

    fig_forecast = go.Figure()


    fig_forecast.add_trace(go.Scatter(
        x=pd.concat([forecast['ds'], forecast['ds'][::-1]]),
        y=pd.concat([forecast['yhat_upper'], forecast['yhat_lower'][::-1]]),
        fill='toself', fillcolor='rgba(52,152,219,0.15)',
        line=dict(color='rgba(255,255,255,0)'),
        name='80% confidence range', showlegend=True
    ))


    fig_forecast.add_trace(go.Scatter(
        x=forecast['ds'], y=forecast['yhat'],
        name='Forecast', line=dict(color='#3498DB', width=2, dash='dash')
    ))
  
    fig_forecast.add_trace(go.Scatter(
        x=prophet_df['ds'], y=prophet_df['y'],
        name='Actual (2024)', mode='lines+markers',
        line=dict(color='#E74C3C', width=2), marker=dict(size=7)
    ))
    fig_forecast.add_vline(
        x=pd.Timestamp('2024-12-01').timestamp() * 1000,
        line_dash='dot', line_color='gray',
        annotation_text='Forecast starts', annotation_position='top right'
    )
    fig_forecast.update_layout(
        title=f'Forecast: {forecast_target.replace("_", " ")} — Jan–Dec 2025',
        xaxis_title='Month', yaxis_title='Predicted encounters',
        hovermode='x unified', height=420
    )
    st.plotly_chart(fig_forecast, use_container_width=True, key="fig_forecast")

  
    st.subheader("Forecast values (Jan–Dec 2025)")
    future_only = forecast[forecast['ds'] > '2024-12-01'][
        ['ds', 'yhat', 'yhat_lower', 'yhat_upper']
    ].copy()
    future_only.columns = ['Month', 'Predicted', 'Lower bound', 'Upper bound']
    future_only['Month'] = future_only['Month'].dt.strftime('%B %Y')
    future_only[['Predicted', 'Lower bound', 'Upper bound']] = \
        future_only[['Predicted', 'Lower bound', 'Upper bound']].round(1)
    st.dataframe(future_only, use_container_width=True, hide_index=True)

except ImportError:
    st.warning("Prophet not installed. Run: `pip install prophet` then restart.")



st.markdown("---")
st.subheader("Patient admission risk scoring (XGBoost)")
st.caption("Predicts which patients are at highest risk of emergency admission — "
           "based on conditions, frailty, age, deprivation and care history")


high_risk   = 0
med_risk    = 0
low_risk    = 0
latest_data = None

try:
    import xgboost as xgb

    df_activity_copy = df_activity.copy()
    df_activity_copy['ACTIVITY_MONTH']    = pd.to_datetime(df_activity_copy['ACTIVITY_MONTH'])
    df_activity_copy['SK_PATIENT_ID_STR'] = 'P' + df_activity_copy['SK_PATIENT_ID'].astype(str)

    df_person_copy = df_person.copy()
    df_person_copy['ANALYSIS_MONTH'] = pd.to_datetime(df_person_copy['ANALYSIS_MONTH'])

    df_merged_ml = pd.merge(
        df_activity_copy,
        df_person_copy[[
            'PERSON_ID', 'ANALYSIS_MONTH', 'AGE', 'GENDER',
            'IMD_QUINTILE_19', 'TOTAL_ACTIVE_CONDITIONS', 'HAS_FRAIL',
            'HAS_COPD', 'HAS_HTN', 'HAS_CHD', 'HAS_AF',
            'HAS_DM', 'HAS_CKD', 'HAS_DEP', 'HAS_SMI'
        ]],
        left_on=['SK_PATIENT_ID_STR', 'ACTIVITY_MONTH'],
        right_on=['PERSON_ID', 'ANALYSIS_MONTH'],
        how='left'
    )

    df_merged_ml['GENDER_ENC']    = (df_merged_ml['GENDER'] == 'Male').astype(int)
    df_merged_ml['HAS_FRAIL_ENC'] = df_merged_ml['HAS_FRAIL'].astype(int)

    feature_cols = [
        'AGE', 'GENDER_ENC', 'IMD_QUINTILE_19', 'TOTAL_ACTIVE_CONDITIONS',
        'HAS_FRAIL_ENC', 'HAS_COPD', 'HAS_HTN', 'HAS_CHD', 'HAS_AF',
        'HAS_DM', 'HAS_CKD', 'HAS_DEP', 'HAS_SMI',
        'GP_ENCOUNTERS', 'CC_ENCOUNTERS', 'AE_ENCOUNTERS', 'OP_ENCOUNTERS',
        'IP_ENCOUNTERS', 'TOTAL_COST'
    ]

  
    df_merged_ml['TARGET'] = (df_merged_ml['IP_NEL_EMERGENCY_ENCOUNTERS'] > 0).astype(int)
    model_df = df_merged_ml[
        feature_cols + ['TARGET', 'SK_PATIENT_ID', 'ACTIVITY_MONTH']
    ].dropna()

    X = model_df[feature_cols].astype(float)
    y = model_df['TARGET']

    model_xgb = xgb.XGBClassifier(
        n_estimators=100, max_depth=3, learning_rate=0.1,
        use_label_encoder=False, eval_metric='logloss',
        random_state=42, verbosity=0
    )
    model_xgb.fit(X, y)

  
    latest_month = model_df['ACTIVITY_MONTH'].max()
    latest_data  = model_df[model_df['ACTIVITY_MONTH'] == latest_month].copy()
    latest_X     = latest_data[feature_cols].astype(float)

    latest_data['RISK_SCORE'] = model_xgb.predict_proba(latest_X)[:, 1]
    latest_data['RISK_LABEL'] = pd.cut(
        latest_data['RISK_SCORE'],
        bins=[0, 0.3, 0.6, 1.0],
        labels=['Low', 'Medium', 'High']
    )

    risk_table = latest_data[[
        'SK_PATIENT_ID', 'RISK_SCORE', 'RISK_LABEL',
        'TOTAL_ACTIVE_CONDITIONS', 'AGE'
    ]].sort_values('RISK_SCORE', ascending=False).reset_index(drop=True)

    risk_table['RISK_SCORE'] = (risk_table['RISK_SCORE'] * 100).round(1)
    risk_table.columns = ['Patient ID', 'Risk score (%)', 'Risk level',
                          'Active conditions', 'Age']

    high_risk = (latest_data['RISK_LABEL'] == 'High').sum()
    med_risk  = (latest_data['RISK_LABEL'] == 'Medium').sum()
    low_risk  = (latest_data['RISK_LABEL'] == 'Low').sum()

    col1, col2, col3 = st.columns(3)
    with col1: st.metric("High risk patients",   f"{high_risk}")
    with col2: st.metric("Medium risk patients", f"{med_risk}")
    with col3: st.metric("Low risk patients",    f"{low_risk}")

    def colour_risk(val):
        if val == 'High':   return 'background-color: #ffd6d6; color: #8b0000'
        if val == 'Medium': return 'background-color: #fff4cc; color: #7a5c00'
        return 'background-color: #d6f5e3; color: #1a5c35'

    styled = risk_table.style.map(colour_risk, subset=['Risk level'])
    st.dataframe(styled, use_container_width=True, hide_index=True)

    st.subheader("What drives emergency admission risk?")
    importance_df = pd.DataFrame({
        'Feature':    feature_cols,
        'Importance': model_xgb.feature_importances_
    }).sort_values('Importance', ascending=True).tail(12)

    fig_imp = px.bar(
        importance_df, x='Importance', y='Feature', orientation='h',
        title='Top feature importance — XGBoost emergency admission risk model',
        color='Importance', color_continuous_scale='Blues'
    )
    fig_imp.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig_imp, use_container_width=True, key="fig_imp")

except ImportError:
    st.warning("XGBoost not installed. Run: `pip install xgboost scikit-learn` then restart.")



st.markdown("---")
st.subheader("Pathway change detection (LSTM)")
st.caption("Detects shifts in a patient's care pathway — "
           "e.g. moving from GP-managed to frequent A&E attender")

flagged = pd.DataFrame()   

try:
    import tensorflow as tf                                  
    from tensorflow.keras.models import Sequential             
    from tensorflow.keras.layers import LSTM, Dense, Dropout  
    from sklearn.preprocessing import MinMaxScaler

    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

    SEQUENCE_LEN = 3
    pathway_cols = ['GP_ENCOUNTERS', 'CC_ENCOUNTERS',
                    'IP_ENCOUNTERS', 'AE_ENCOUNTERS', 'OP_ENCOUNTERS']

    df_seq = df_activity.copy()
    df_seq['ACTIVITY_MONTH'] = pd.to_datetime(df_seq['ACTIVITY_MONTH'])
    df_seq = df_seq.sort_values(['SK_PATIENT_ID', 'ACTIVITY_MONTH'])

    scaler = MinMaxScaler()
    df_seq[pathway_cols] = scaler.fit_transform(df_seq[pathway_cols].fillna(0))

    X_seq, y_seq, meta = [], [], []
    for pid, grp in df_seq.groupby('SK_PATIENT_ID'):
        grp    = grp.sort_values('ACTIVITY_MONTH').reset_index(drop=True)
        vals   = grp[pathway_cols].values
        months = grp['ACTIVITY_MONTH'].values
        for i in range(len(vals) - SEQUENCE_LEN):
            X_seq.append(vals[i:i + SEQUENCE_LEN])
            y_seq.append(vals[i + SEQUENCE_LEN])
            meta.append({'patient_id': pid, 'predict_month': months[i + SEQUENCE_LEN]})

    X_seq = np.array(X_seq)
    y_seq = np.array(y_seq)

    lstm_model = Sequential([
        LSTM(32, input_shape=(SEQUENCE_LEN, len(pathway_cols)), return_sequences=False),
        Dropout(0.2),
        Dense(len(pathway_cols))
    ])
    lstm_model.compile(optimizer='adam', loss='mse')
    lstm_model.fit(X_seq, y_seq, epochs=50, batch_size=8, verbose=0)

    preds     = lstm_model.predict(X_seq, verbose=0)
    errors    = np.mean(np.abs(preds - y_seq), axis=1)
    threshold = errors.mean() + 1.5 * errors.std()

    meta_df = pd.DataFrame(meta)
    meta_df['reconstruction_error'] = errors
    meta_df['pathway_change'] = meta_df['reconstruction_error'] > threshold
    meta_df['predict_month']  = pd.to_datetime(meta_df['predict_month'])

    pivot_error = meta_df.pivot_table(
        index='patient_id', columns='predict_month',
        values='reconstruction_error'
    )
    pivot_error.columns = [pd.Timestamp(c).strftime('%b %Y') for c in pivot_error.columns]

    fig_lstm = go.Figure(data=go.Heatmap(
        z=pivot_error.values,
        x=pivot_error.columns.tolist(),
        y=[f'P{int(p)}' for p in pivot_error.index],
        colorscale='RdYlGn_r',
        colorbar=dict(title='Anomaly score'),
        text=pivot_error.values.round(3),
        texttemplate='%{text}', textfont=dict(size=9)
    ))
    fig_lstm.update_layout(
        title='Pathway anomaly score by patient and month (red = likely change)',
        xaxis_title='Month', yaxis_title='Patient ID',
        height=max(350, len(pivot_error) * 30)
    )
    st.plotly_chart(fig_lstm, use_container_width=True, key="fig_lstm")

    flagged = meta_df[meta_df['pathway_change']].copy()
    flagged['predict_month']        = flagged['predict_month'].dt.strftime('%B %Y')
    flagged['reconstruction_error'] = flagged['reconstruction_error'].round(4)
    flagged.columns = ['Patient ID', 'Month', 'Anomaly score', 'Flagged as change']

    if flagged.empty:
        st.success("No significant pathway changes detected in 2024.")
    else:
        st.warning(f"{len(flagged)} pathway change(s) flagged — review below")
        st.dataframe(
            flagged[['Patient ID', 'Month', 'Anomaly score']],
            use_container_width=True, hide_index=True
        )

except ImportError:
    st.warning("TensorFlow not installed. Run: `pip install tensorflow` then restart.")



st.markdown("---")
st.subheader("Automated workforce insights summary")
st.caption("Generated from your data — no hardcoded values")

total_encounters_yr = int(workforce['Total_Encounters'].sum())
total_hours_yr      = int(workforce['Total_Hours'].sum())
total_cost_yr       = workforce['Total_Cost'].sum()
peak_month_wf       = workforce.loc[workforce['Total_Encounters'].idxmax(), 'ACTIVITY_MONTH']
lowest_month_wf     = workforce.loc[workforce['Total_Encounters'].idxmin(), 'ACTIVITY_MONTH']
peak_label          = pd.Timestamp(peak_month_wf).strftime('%B %Y')
lowest_label        = pd.Timestamp(lowest_month_wf).strftime('%B %Y')
gp_share_pct        = workforce['GP_Hours'].sum() / workforce['Total_Hours'].sum() * 100
cc_share_pct        = workforce['CC_Hours'].sum() / workforce['Total_Hours'].sum() * 100

sum_col1, sum_col2 = st.columns(2)

with sum_col1:
    st.info(f"""
**Workforce utilisation — 2024**

- Total encounters across all services: **{total_encounters_yr:,}**
- Total staff hours utilised: **{total_hours_yr:,} hours**
- GP accounted for **{gp_share_pct:.0f}%** of all staff hours
- Community care accounted for **{cc_share_pct:.0f}%** of all staff hours
- Busiest month: **{peak_label}** ({int(workforce['Total_Encounters'].max())} encounters)
- Quietest month: **{lowest_label}** ({int(workforce['Total_Encounters'].min())} encounters)
- Total cost across all services: **£{total_cost_yr:,.0f}**
""")

with sum_col2:
    if latest_data is not None:
        high_pct = high_risk / len(latest_data) * 100
        st.warning(f"""
**Risk model findings**

- **{high_risk}** patient(s) flagged as HIGH risk for emergency admission ({high_pct:.0f}% of cohort)
- **{med_risk}** patient(s) at MEDIUM risk
- Top risk drivers: see feature importance chart above
- Recommend proactive review of high-risk patients before next month
""")
    else:
        st.info("Install XGBoost to see risk model findings.")

if not flagged.empty:
    st.error(f"""
**Pathway change alerts (LSTM)**

- **{len(flagged)}** patient-month(s) flagged as significant pathway change
- These patients have shifted away from their established care pattern
- Recommend clinical review to confirm whether the change reflects a planned intervention or unplanned escalation
""")
else:
    st.success("**Pathway change alerts:** No significant pathway changes detected in 2024.")