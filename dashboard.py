import pandas as pd # pandas is a data manipulation and analysis library.
import numpy as np # numpy is for multidimensional array manipulation.
import streamlit as st #installing streamlit as st. Streamlit is for hosting the dashboard.
import plotly.express as px # accessing plotly's inbuilt charts for data visualisation.
import plotly.graph_objects as go # customising multiple data charts for data visualiusation for my dashboard

# setting the page configuration
st.set_page_config(
  page_title="Heart Failure Workforce Utilisation Tool",
  layout="wide"
)
# HEAD

# Initialisation of session state for navigation
if 'current_page' not in st.session_state:
  st.session_state.current_page = "Hospital activity"

# Loading my dashboard data
@st.cache_data # cache data is used for better performance. 
def loadData():
    df_person=pd.read_excel ('Heart_Failure_Patient_Data_12_Months_20_Patients.xlsx', sheet_name ='PERSON_MONTH_DATA') # df - data frame, pd - pandas object. read_excel allows me to open and read the data in my excel spreadsheet and use it in the code.
   # df_person # Data frame is a data structure for storing tabular data in Python.
   # print (df_person)
    # The difference between df and print(df) is df is evaluating the object, i.e. it is displaying it in a pretty table format, whereas print(df) is printing it as text.

    df_activity=pd.read_excel ('Heart_Failure_Patient_Data_12_Months_20_Patients.xlsx', sheet_name ='FCT_ACTIVITY_DATA') # loading the activity data for the dashboard.
    # print(df_activity)
    
    df_activity_catalogue=pd.read_excel ('Heart_Failure_Patient_Data_12_Months_20_Patients.xlsx', sheet_name ='FCT_ACTIVITY_CATALOGUE') # loading the activity catalogue data for the dashboard.
    # print(df_activity_catalogue)
    
    df_person_month_catalogue=pd.read_excel ('Heart_Failure_Patient_Data_12_Months_20_Patients.xlsx', sheet_name ='PERSON_MONTH_CATALOGUE') # loading the person month catalogue data for the dashboard.
    print(df_person_month_catalogue)
    
    df_activity['ACTIVITY_MONTH'] = pd.to_datetime(df_activity['ACTIVITY_MONTH'])
    df_person['ANALYSIS_MONTH'] = pd.to_datetime(df_person['ANALYSIS_MONTH'])
    
    return df_person, df_activity, df_activity_catalogue, df_person_month_catalogue

df_person, df_activity, df_activity_catalogue, df_person_month_catalogue = loadData()
st.success(f"Loaded {len(df_person)} person records and {len(df_activity)} activity records")

# Adding navigational sidebar on dashboard
with st.sidebar:
  st.title("Dashboards")
  
  pages = [
    "Hospital activity",
    "GP activity",
    "Community provider activity"
  ]
  
  for page in pages: 
    if st.button(
      page,
      key=page,
      width=True,
      use_container_width=True,
      type="primary" if st.session_state.current_page == page else "secondary"
    ):
      st.session_state.current_page = page
      st.rerun()

st.markdown("---")

# Getting the current session from session state
section = st.session_state.current_page

    
# Displaying the contents of each section of the dashboard
if section == ("Hospital activity"):
      st.header("Hospital activity")
      st.subheader("Hospital metrics")
      # create 7 columns for the hospital metrics
      col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

      with col1: 
        total_admissions = df_activity['IP_ENCOUNTERS'].sum()
        st.metric(
          label="Total Admissions",
          value=f"{int(total_admissions)}"
        )
        
      with col2: 
        emergency_admissions = df_activity['IP_NEL_EMERGENCY_ENCOUNTERS'].sum()
        st.metric(
          label="Emergency Admissions",
          value=f"{int(emergency_admissions)}"
        )
        
      with col3: 
        elective_admissions = df_activity['IP_EL_ENCOUNTERS'].sum()
        st.metric(
          label="Elective Admissions",
          value=f"{int(elective_admissions)}"
        )
        
      with col4: 
        total_duration = df_activity['IP_DURATION'].sum()
        total_encounters = df_activity['IP_ENCOUNTERS'].sum()
        avg_los = total_duration / total_encounters if total_encounters > 0 else 0
        st.metric(
          label="Average length of stays",
          value=f"{avg_los:.1f} days"
        )
        
      with col5: 
        total_ip_cost = df_activity['IP_COST'].sum()
        st.metric(
          label="Total Inpatient Cost",
          value=f"£{total_ip_cost:,.0f}"
        )
        
      with col6: 
        total_ae = df_activity['AE_ENCOUNTERS'].sum()
        st.metric(
          label="A&E Attendances",
          value=f"{int(total_ae)}"
        )
        
      with col7:
        total_ae_cost = df_activity['AE_COST'].sum()
        st.metric(
          label="A&E Cost",
          value=f"£{total_ae_cost:,.0f}"
        )
      # calculating the total A&E cost. 

      st.markdown("---")

      # Adding my data visualisations here for the dashboard results as graphs and objects using plotly. 
      # st. header("Hospital activity analysis")
      
      # Chart one: monthly hospital addmissions data. 
      st.subheader("Monthly Admissions Trends")

      monthly_admissions = df_activity.groupby('ACTIVITY_MONTH').agg({
        'IP_NEL_EMERGENCY_ENCOUNTERS': 'sum',
        'IP_EL_ENCOUNTERS': 'sum'
      }).reset_index()

      figure1 = go.Figure()

      figure1.add_trace(go.Scatter(
        x=monthly_admissions['ACTIVITY_MONTH'],
        y=monthly_admissions['IP_NEL_EMERGENCY_ENCOUNTERS'],
        name='Emergency Admissions',
        mode='lines+markers',
        line=dict(color="#3336CB", width=3),
        marker=dict(size=8)
      ))

      figure1.add_trace(go.Scatter(
        x=monthly_admissions['ACTIVITY_MONTH'],
        y=monthly_admissions["IP_EL_ENCOUNTERS"],
        name='Elective Admissions',
        mode='lines+markers',
        line=dict(color="#33CBC8", width=3),
        marker=dict(size=8)
      ))

      st.plotly_chart(figure1, use_container_width=True, key="figure1")

      # Chart 2: A&E and Inpatient Activity
      st.subheader("A&E and Inpatient Activity")

      ae_ip_activity = df_activity.groupby('ACTIVITY_MONTH').agg({
        'AE_EMERGENCY_ENCOUNTERS': 'sum',
        'AE_URGENT_ENCOUNTERS': 'sum',
        'IP_ENCOUNTERS': 'sum'
      }).reset_index()

      figure2 = go.Figure()

      figure2.add_trace(go.Bar(
        x=ae_ip_activity['ACTIVITY_MONTH'],
        y=ae_ip_activity['AE_URGENT_ENCOUNTERS'],
        name='A&E Urgent',
        marker_color="#CB3833"
      ))

      figure2.add_trace(go.Bar(
        x=ae_ip_activity['ACTIVITY_MONTH'],
        y=ae_ip_activity['AE_EMERGENCY_ENCOUNTERS'],
        name='A&E Emergency',
        marker_color="#CB3391"
      ))

      figure2.add_trace(go.Bar(
        x=ae_ip_activity['ACTIVITY_MONTH'],
        y=ae_ip_activity['IP_ENCOUNTERS'],
        name='Inpatient Admissions',
        marker_color="#9E9FBF"
      ))

      figure2.update_layout(
        barmode='stack',
        title='Total Emergency Care For Each Month',
        xaxis_title='Month',
        yaxis_title='Number of Encounters',
        hovermode='x unified',
        height=400
      )

      st.plotly_chart(figure2, use_container_width=True,key="figure2")

      # Chart 3 Time of Stay in Hospital
      st.subheader("Time of Stay in Hospital")

      los_data = []

      for idx, row in df_activity.iterrows():
        if row['IP_NEL_EMERGENCY_ENCOUNTERS'] > 0 and row['IP_NEL_EMERGENCY_DURATION'] > 0:
          avg_los_emergency = row['IP_NEL_EMERGENCY_DURATION'] / row['IP_NEL_EMERGENCY_ENCOUNTERS']
          for _ in range(int(row['IP_NEL_EMERGENCY_ENCOUNTERS'])):
            los_data.append({
              'Admission Type': 'Emergency',
              'Length of Stay (days)': avg_los_emergency
            })
        
        if row['IP_EL_ENCOUNTERS'] > 0 and row['IP_EL_DURATION']:
          avg_los_elective = row['IP_DURATION'] / row['IP_EL_ENCOUNTERS']
          for _ in range(int(row['IP_EL_ENCOUNTERS'])):
            los_data.append({
              'Admission Type': 'Elective',
              'Length of Stay (days)': avg_los_elective
            })
      los_df = pd.DataFrame(los_data)
      
      figure3 = px.box(
        los_df,
        x='Admission Type',
        y='Length of Stay (days)',
        color='Admission Type', 
        color_discrete_map={'Emergency': "#CB3333", 'Elective': "#CB5E33"},
        title='Length of Stay: Emergency and Elective Admissions'
      )
      figure3.update_layout(showlegend=False, height=400)
      
      st.plotly_chart(figure3, use_container_width=True, keys="figure3")
      
      #Chart 4 Readmissions Analysis
      st.subheader("4 Readmissions Analysis - Frequently Admitted")
      
      df_activity['ACTIVITY_MONTH'] = pd.to_datetime(df_activity['ACTIVITY_MONTH'], errors='coerce')
      readmission_data = df_activity.loc[df_activity['IP_ENCOUNTERS'] > 0].copy()
      readmission_data['Month'] = readmission_data['ACTIVITY_MONTH'].dt.strftime('%b %Y')
      
      readmission_pivot = readmission_data.pivot_table(
        values='IP_ENCOUNTERS',
        index='SK_PATIENT_ID',
        columns='Month',
        aggfunc='sum',
        fill_value=0
      )
      #Filtering and sorting
      readmission_pivot = readmission_pivot.loc[readmission_pivot.sum(axis=1) >= 2]
      
      readmission_pivot['Total'] = readmission_pivot.sum(axis=1)
      readmission_pivot = readmission_pivot.sort_values('Total', ascending=False).drop(columns=['Total'])
      
      #Check to see if there are no patients that qualify, then show message identifying this.
      if readmission_pivot.empty:
        st.info("No patients had two or more inpatient admissions in the 12 month/year period.")
      else: 
      
        figure4 = go.Figure(data=go.Heatmap(
        z=readmission_pivot.values,
        x=readmission_pivot.columns,
        y=readmission_pivot.index,
        colorscale='Blues',
        text=readmission_pivot.values,
        texttemplate='%{text}',
        textfont={"size": 10},
        colorbar=dict(title="Admissions")
      ))
      
      figure4.update_layout(
        title='Patient Readmission Patterns (patients with two or more further admissions)',
        xaxis_title='Month',
        yaxis_title='Patient ID',
        height=max(400, len(readmission_pivot) * 25)
      )
      
      st.plotly_chart(figure4, use_container_width=True, keys="figure4")
      
      # Chart 5 Breakdown of Costs
      st.subheader("Breakdown of Costs: Emergency and Elective")
      
      emergency_cost = df_activity['IP_NEL_EMERGENCY_COST'].sum()
      elective_cost = df_activity['IP_EL_COST'].sum()
      
      cost_breakdown = pd.DataFrame({
        'Type' : ['Emergency Admissions', 'Elective Admissions'],
        'Cost' : [emergency_cost, elective_cost]
      })
      
      figure5 = px.pie(
        cost_breakdown,
        values='Cost',
        names='Type',
        title='Inpatient Cost Distribution',
        color='Type',
        color_discrete_map={
          'Emergency Admissions': '#3336CB',
          'Elective Admissions': '#3336CB'
        }
      )

      figure5.update_layout(height=400)

      st.plotly_chart(figure5, use_container_width=True, keys="figure5")

      # Chart 6 Top Highest Cost Patients

      st.subheader("Top Highest Cost Patients")

      df_activity["SK_PATIENT_ID_STR"] = "P" + df_activity["SK_PATIENT_ID"].astype("string")

      df_merged = pd.merge(
        df_activity,
        df_person[['PERSON_ID', 'ANALYSIS_MONTH', 'TOTAL_ACTIVE_CONDITIONS']],
        left_on=['SK_PATIENT_ID_STR', 'ACTIVITY_MONTH'],
        right_on=['PERSON_ID', 'ANALYSIS_MONTH'],
        how='left'
      )

      patient_costs = df_merged.groupby('SK_PATIENT_ID').agg({
        'IP_COST': 'sum',
        'TOTAL_ACTIVE_CONDITIONS': 'mean'
      }).reset_index()

      top_10_patients = patient_costs.nlargest(10, 'IP_COST')

      figure6 = px.bar(
        top_10_patients,
        x='SK_PATIENT_ID',
        y='IP_COST',
        color='TOTAL_ACTIVE_CONDITIONS',
        title='Top 10 Higest Cost Patients (by Inpatient Cost)',
        labels={
          'SK_PATIENT_ID': 'Patient ID',
          'IP_COST': 'Total Inpatient Cost (£)',
          'TOTAL_ACTIVE_CONDITIONS': 'Number of Conditions'
        },
        color_continuous_scale='Blues',
        text='IP_COST'
      )

      figure6.update_layout(
        xaxis_title='Patient ID',
        yaxis_title='Total Inpatient Cost (£)', 
        height=450
      )

      st.plotly_chart(figure6, use_container_width=True, keys="figure6")

      # Main Insights
      st.markdown("---")
      st.subheader("Main Insights")
        
      col1, col2 = st.columns(2)
        
      with col1:
          st.info
        
        # Showing sample data from my Excel spreadsheet
        # st.dataframe(df_activity.head())


# Initialisation of session state for navigation
if 'current_page'not in st.session_state:
  st.session_state.current_page = "Hospital activity"

# Loading my dashboard data
def loadData():
    df_person=pd.read_excel ('Heart_Failure_Patient_Data_12_Months_20_Patients.xlsx', sheet_name ='PERSON_MONTH_DATA') # df - data frame, pd - pandas object. read_excel allows me to open and read the data in my excel spreadsheet and use it in the code.
#     df_person # Data frame is a data structure for storing tabular data in Python.
#     print (df_person)
#     # The difference between df and print(df) is df is evaluating the object, i.e. it is displaying it in a pretty table format, whereas print(df) is printing it as text.

#     df_activity=pd.read_excel ('Heart_Failure_Patient_Data_12_Months_20_Patients.xlsx', sheet_name ='FCT_ACTIVITY_DATA') # loading the activity data for the dashboard.
#     print(df_activity)
    
#     df_activity_catalogue=pd.read_excel ('Heart_Failure_Patient_Data_12_Months_20_Patients.xlsx', sheet_name ='FCT_ACTIVITY_CATALOGUE') # loading the activity catalogue data for the dashboard.
#     print(df_activity_catalogue)
    
#     df_person_month_catalogue=pd.read_excel ('Heart_Failure_Patient_Data_12_Months_20_Patients.xlsx', sheet_name ='PERSON_MONTH_CATALOGUE') # loading the person month catalogue data for the dashboard.
#     print(df_person_month_catalogue)
#     return df_person, df_activity, df_activity_catalogue, df_person_month_catalogue

# df_person, df_activity, df_activity_catalogue, df_person_month_catalogue = loadData()
# st.success(f"Loaded {len(df_person)} person records and {len(df_activity)} activity records")

# # Adding navigational sidebar on dashboard
# with st.sidebar:
#   st.title("Dashboards")
  
#   pages = [
#     "Hospital activity",
#     "GP activity",
#     "Community provider activity"
#   ]
  
#   for page in pages: 
#     if st.button(
#       page,
#       key=page,
#       use_container_width=True,
#       type="primary" if st.session_state.current_page == page else "secondary"
#     ):
#       st.session_state.current_page = page
#       st.rerun()

# st.markdown("---")

# # Getting the current session from session state
# section = st.session_state.current_page

    
# # Displaying the contents of each section of the dashboard
# if section == ("Hospital activity"):
#   st.header("Hospital activity")
#   st.subheader("Hospital metrics")
#   # create 7 columns for the hospital metrics
#   col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
  
#   with col1: 
#     total_admissions = df_activity['IP_ENCOUNTERS'].sum()
#     st.metric(
#       label="Total Admissions",
#       value=f"{int(total_admissions)}"
#     )
    
#   with col2: 
#     emergency_admissions = df_activity['IP_NEL_EMERGENCY_ENCOUNTERS'].sum()
#     st.metric(
#       label="Emergency Admissions",
#       value=f"{int(emergency_admissions)}"
#     )
    
#   with col3: 
#     elective_admissions = df_activity['IP_EL_ENCOUNTERS'].sum()
#     st.metric(
#       label="Elective Admissions",
#       value=f"{int(elective_admissions)}"
#     )
    
#   with col4: 
#     total_duration = df_activity['IP_DURATION'].sum()
#     total_encounters = df_activity['IP_ENCOUNTERS'].sum()
#     avg_los = total_duration / total_encounters if total_encounters > 0 else 0
#     st.metric(
#       label="Average length of stays",
#       value=f"{avg_los:.1f} days"
#     )
    
#   with col5: 
#     total_ip_cost = df_activity['IP_COST'].sum()
#     st.metric(
#       label="Total Inpatient Cost",
#       value=f"£{total_ip_cost:,.0f}"
#     )
    
#   with col6: 
#     total_ae = df_activity['AE_ENCOUNTERS'].sum()
#     st.metric(
#       label="A&E Attendances",
#       value=f"{int(total_ae)}"
#     )
    
#   with col7:
#     total_ae_cost = df_activity['AE_COST'].sum()
#     st.metric(
#       label="A&E Cost",
#       value=f"£{total_ae_cost:,.0f}"
#     )
# # calculating the total A&E cost. 

#   st.markdown("---")


  
#   # Showing sample data from my Excel spreadsheet
#   # st.dataframe(df_activity.head())

  
# elif section == "GP activity": 
#   st.header("GP activity")
#   st.write("GP activity contents will be displayed here")
#   # Showing some sample data from my Excel spreadsheet
#   #st.dataframe(df_person.head())
  
# elif section == "Community provider activity":
#   st.header("Community provider activity")
#   st.write("Community provider activity contents will be displayed here")
#   # df_person, df_activity, df_activity_catalogue, df_person_month_catalogue = loadData()
#   # Showing some sample data from my Excel spreadsheet
#   # st.metric("Total cost", f"£{df_activity['total cost'].sum():,.2f}") 
  
# # Displaying the contents of each section of the dashboard

  
# Section 2: GP Activity
    