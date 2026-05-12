import os
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(
    page_title="RAG Chatbot — Heart Failure",
    layout="wide"
)
with st.sidebar:
    st.title("Settings")
    st.markdown("**ollama Model**")
    st.markdown(
        "ollama runs AI locally on your Mac — free, no internet, no API key.\n\n"
        "Pull a model once with:\n"
        "```\nollama pull llama3.2\n```"
    )
    ollama_model=st.selectbox(
        "Select model",
        options=["llama3.2", "llama3.1", "mistral", "phi3", "gemma2"],
        index=0,
        help="Must match a model you have pulled with 'ollama pull <name>'"
    )
    st.info(
        f"Using: **{ollama_model}**\n\n"
        "Make sure `ollama serve` is running in a separate terminal."
    )
EXCEL_FILE='Heart_Failure_Patient_Data_12_Months_20_Patients.xlsx'
@st.cache_data
def load_data():
    df_person=pd.read_excel(EXCEL_FILE, sheet_name='PERSON_MONTH_DATA')
    df_activity=pd.read_excel(EXCEL_FILE, sheet_name='FCT_ACTIVITY_DATA')
    df_activity['ACTIVITY_MONTH']=pd.to_datetime(df_activity['ACTIVITY_MONTH'])
    df_person['ANALYSIS_MONTH']=pd.to_datetime(df_person['ANALYSIS_MONTH'])
    return df_person, df_activity
df_person, df_activity=load_data()
workforce=df_activity.groupby('ACTIVITY_MONTH').agg(
    GP_Encounters=('GP_ENCOUNTERS', 'sum'),
    CC_Encounters=('CC_ENCOUNTERS', 'sum'),
    IP_Encounters=('IP_ENCOUNTERS', 'sum'),
    AE_Encounters=('AE_ENCOUNTERS', 'sum'),
    OP_Encounters=('OP_ENCOUNTERS', 'sum'),
    MH_Encounters=('MH_ENCOUNTERS', 'sum'),
    GP_Hours=('GP_DURATION',   lambda x: x.sum() / 60),
    CC_Hours=('CC_DURATION',   lambda x: x.sum() / 60),
    IP_Hours=('IP_DURATION',   lambda x: x.sum() / 60),
    AE_Hours=('AE_DURATION',   lambda x: x.sum() / 60),
    OP_Hours=('OP_DURATION',   lambda x: x.sum() / 60),
    Total_Cost=('TOTAL_COST',    'sum'),
).reset_index()
workforce['Total_Hours']=(
    workforce['GP_Hours'] + workforce['CC_Hours'] +
    workforce['IP_Hours'] + workforce['AE_Hours'] +
    workforce['OP_Hours']
)
workforce['Total_Encounters']=(
    workforce['GP_Encounters'] + workforce['CC_Encounters'] +
    workforce['IP_Encounters'] + workforce['AE_Encounters'] +
    workforce['OP_Encounters'] + workforce['MH_Encounters']
)
high_risk=0
med_risk=0
latest_data=None
flagged=pd.DataFrame()
st.header("Workforce Planning & Predictions")
st.caption("Based on Jan 2024 – Dec 2024 | 20 heart failure patients | All services")
st.markdown("---")
st.subheader("Ask your data a question (RAG)")
st.caption(
    "Type a clinical question — the assistant retrieves relevant patient data "
    "and generates a grounded answer using a local AI model via ollama"
)
try:
    import chromadb
    from chromadb.utils import embedding_functions
    @st.cache_resource
    def build_vector_store(_df_activity, _df_person):
        client=chromadb.Client()
        emb_fn=embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        collection=client.get_or_create_collection(
            name="patient_profiles",
            embedding_function=emb_fn
        )
        if collection.count() > 0:
            return collection
        docs, doc_ids, metadatas=[], [], []
        for pid in _df_activity['SK_PATIENT_ID'].unique():
            pat_act=_df_activity[_df_activity['SK_PATIENT_ID'] == pid]
            pid_str=f'P{int(pid)}'
            pat_per=_df_person[_df_person['PERSON_ID'] == pid_str]
            if pat_per.empty:
                continue
            pat_per=pat_per.sort_values('ANALYSIS_MONTH').iloc[-1]
            doc=f"""
Patient {pid_str} summary (Jan–Dec 2024):
Age: {pat_per['AGE']}, Gender: {pat_per['GENDER']}, IMD Quintile: {pat_per['IMD_QUINTILE_19']}
Frailty: {pat_per['HAS_FRAIL']}, Active conditions: {int(pat_per['TOTAL_ACTIVE_CONDITIONS'])}
Conditions: COPD={pat_per['HAS_COPD']}, HTN={pat_per['HAS_HTN']}, CHD={pat_per['HAS_CHD']},
  AF={pat_per['HAS_AF']}, DM={pat_per['HAS_DM']}, CKD={pat_per['HAS_CKD']},
  Depression={pat_per['HAS_DEP']}, Heart failure={pat_per['HAS_HF']}
GP visits: {int(pat_act['GP_ENCOUNTERS'].sum())} (avg {pat_act['GP_ENCOUNTERS'].mean():.1f}/month)
Community care contacts: {int(pat_act['CC_ENCOUNTERS'].sum())}
Inpatient admissions: {int(pat_act['IP_ENCOUNTERS'].sum())}
Emergency admissions: {int(pat_act['IP_NEL_EMERGENCY_ENCOUNTERS'].sum())}
A&E attendances: {int(pat_act['AE_ENCOUNTERS'].sum())}
Outpatient appointments: {int(pat_act['OP_ENCOUNTERS'].sum())}
Total cost: £{pat_act['TOTAL_COST'].sum():,.0f}
Peak encounter month: {pat_act.loc[pat_act['TOTAL_ENCOUNTERS'].idxmax(), 'ACTIVITY_MONTH']}
""".strip()
            docs.append(doc)
            doc_ids.append(pid_str)
            metadatas.append({
                'patient_id': pid_str,
                'age':        int(pat_per['AGE']) if pd.notna(pat_per['AGE']) else 0,
                'frail':      str(pat_per['HAS_FRAIL']),
                'conditions': int(pat_per['TOTAL_ACTIVE_CONDITIONS'])
            })
        collection.add(documents=docs, ids=doc_ids, metadatas=metadatas)
        return collection
    collection=build_vector_store(df_activity, df_person)
    if 'rag_messages' not in st.session_state:
        st.session_state.rag_messages=[]
    for msg in st.session_state.rag_messages:
        with st.chat_message(msg['role']):
            st.write(msg['content'])
    st.write("**Try asking:**")
    example_cols=st.columns(3)
    examples=[
        "Which patients are at highest risk of readmission?",
        "Who has the most comorbidities and how does that affect their GP use?",
        "Which frail patients have the highest A&E attendance?"
    ]
    for i, (ecol, q) in enumerate(zip(example_cols, examples)):
        with ecol:
            if st.button(q, key=f"ex_{i}", use_container_width=True):
                st.session_state.rag_messages.append({'role': 'user', 'content': q})
                st.rerun()
    user_question=st.chat_input("Ask a question about your heart failure cohort...")
    if user_question:
        st.session_state.rag_messages.append({'role': 'user', 'content': user_question})
        # Retrieve the 5 most semantically relevant patient profiles
        results=collection.query(query_texts=[user_question], n_results=5)
        retrieved_context="\n\n---\n\n".join(results['documents'][0])
        system_prompt="""You are a clinical data analyst assistant for a heart failure service.
You are given retrieved patient summaries from a real dataset covering Jan–Dec 2024.
Answer the user's question using ONLY the provided patient data.
Be specific, cite patient IDs where relevant, and highlight clinical insights.
Keep answers concise (3–5 sentences). Do not make up any data."""
        try:
            import ollama
            with st.spinner(f"Thinking with {ollama_model}..."):
                response=ollama.chat(
                    model=ollama_model,
                    messages=[
                        {'role': 'system', 'content': system_prompt},
                        {
                            'role': 'user',
                            'content': (
                                f"Retrieved patient data:\n{retrieved_context}"
                                f"\n\nQuestion: {user_question}"
                            )
                        }
                    ]
                )
            answer=response['message']['content']
        except ImportError:
            st.error(
                "ollama Python package not installed. "
                "Run: `pip install ollama` then restart."
            )
            st.stop()
        except Exception as e:
            error_str=str(e).lower()
            if "connection" in error_str or "refused" in error_str:
                st.error(
                    "**ollama is not running.**\n\n"
                    "Open a new terminal and run:\n"
                    "```\nollama serve\n```\n"
                    "Keep that terminal open, then ask your question again."
                )
            elif "model" in error_str or "not found" in error_str:
                st.error(
                    f"**Model `{ollama_model}` not found.**\n\n"
                    f"Run this in your terminal to download it:\n"
                    f"```\nollama pull {ollama_model}\n```\n"
                    "Then ask your question again."
                )
            else:
                st.error(f"ollama error: {e}")
            st.stop()
        st.session_state.rag_messages.append({'role': 'assistant', 'content': answer})
        with st.expander("View retrieved patient profiles used to answer"):
            for i, doc in enumerate(results['documents'][0]):
                st.text(f"Patient {results['ids'][0][i]}:\n{doc}\n")
        st.rerun()
    # Clear conversation button
    if st.session_state.rag_messages:
        if st.button("Clear conversation"):
            st.session_state.rag_messages=[]
            st.rerun()
except ImportError:
    st.warning(
        "ChromaDB not installed. "
        "Run: `pip install chromadb sentence-transformers` then restart."
    )
st.markdown("---")
st.subheader("Automated workforce insights summary")
st.caption("Generated from your data — no hardcoded values")
total_encounters_yr=int(workforce['Total_Encounters'].sum())
total_hours_yr=int(workforce['Total_Hours'].sum())
total_cost_yr=workforce['Total_Cost'].sum()
peak_month_wf=workforce.loc[workforce['Total_Encounters'].idxmax(), 'ACTIVITY_MONTH']
lowest_month_wf=workforce.loc[workforce['Total_Encounters'].idxmin(), 'ACTIVITY_MONTH']
peak_label=pd.Timestamp(peak_month_wf).strftime('%B %Y')
lowest_label=pd.Timestamp(lowest_month_wf).strftime('%B %Y')
gp_share_pct=workforce['GP_Hours'].sum() / workforce['Total_Hours'].sum() * 100
cc_share_pct=workforce['CC_Hours'].sum() / workforce['Total_Hours'].sum() * 100
sum_col1, sum_col2=st.columns(2)
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
        high_pct=high_risk / len(latest_data) * 100
        st.warning(f"""
**Risk model findings**
- **{high_risk}** patient(s) flagged as HIGH risk for emergency admission ({high_pct:.0f}% of cohort)
- **{med_risk}** patient(s) at MEDIUM risk
- Top risk drivers: run dashboard_ml.py to see the feature importance chart
- Recommend proactive review of high-risk patients before next month
""")
    else:
        st.info(
            "Risk model not run in this file. "
            "Open **dashboard_ml.py** to see XGBoost risk scores."
        )
if not flagged.empty:
    st.error(f"""
**Pathway change alerts (LSTM)**
- **{len(flagged)}** patient-month(s) flagged as significant pathway change
- These patients have shifted away from their established care pattern
- Recommend clinical review to confirm whether the change reflects a planned intervention
  or unplanned escalation
""")
else:
    st.success(
        "Pathway change alerts: No LSTM pathway changes detected. "
        "Run dashboard_ml.py for the full LSTM analysis."
    )