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
      
      st.plotly_chart(figure3, use_container_width=True, key="figure3")
      
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
      
      st.plotly_chart(figure4, use_container_width=True, key="figure4")
      
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
          'Emergency Admissions': "#C00606",
          'Elective Admissions': "#148BA9"
        }
      )

      figure5.update_layout(height=400)

      st.plotly_chart(figure5, use_container_width=True, key="figure5")

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

      st.plotly_chart(figure6, use_container_width=True, key="figure6")

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
if section == "GP activity":
  st.header("GP Activity")
  
  # Metrics row for the GP section
  st.subheader("Key GP Metrics")
  
  # Creating 5 columns for each of the GP metrics
  col1, col2, col3, col4, col5 = st.columns(5)
  
  with col1:
    total_gp = int(df_activity['GP_ENCOUNTERS'].sum())
    st.metric(
      label="Total GP Visits",
      value=f"{total_gp:,}"
    )
  
  with col2:
    avg_per_patient = df_activity.groupby('SK_PATIENT_ID')['GP_ENCOUNTERS'].sum().mean()
    st.metric(
      label="Average visits per patient",
      value=f"{avg_per_patient:.1f}"
    )
    
  with col3: 
    total_gp_duration = df_activity['GP_DURATION'].sum()
    total_gp_hours = total_gp_duration / 60 # Converting minutes to hours for the amount of GP hours
    st.metric(
      label="Total GP consultation hours",
      value=f"{total_gp_hours:,.0f} hours"
    )
    
  with col4:
    avg_consultation = total_gp_duration / total_gp if total_gp > 0 else 0
    st.metric(
      label="Average consultation duration time",
      value=f"{avg_consultation:.1f}"
    )
    
  with col5: 
    # Patients who visit the GP >10 times a month (high utilising patients).
    high_utilizers = df_activity[df_activity['GP_ENCOUNTERS'] > 10].groupby('SK_PATIENT_ID')['ACTIVITY_MONTH'].count()
    st.metric(
      label="High Utilizers (>10/month)",
      value=f"{len(high_utilizers)}"
    )
    
  st.markdown("---")
  
  # GP Visualisations
  st.header("GP Activity Analysis")
  
  # Chart 1: GP Consultation volume trends
  st.subheader("GP Consultation Volume Over The 12 Month/Year period")
  
  #Preparing the Data
  monthly_gp = df_activity.groupby('ACTIVITY_MONTH').agg({
    'GP_ENCOUNTERS': 'sum'
  }).reset_index()
 
  # Create area chart
  figure_gp1 = go.Figure()
  

  figure_gp1.add_trace(go.Scatter(
    x=monthly_gp['ACTIVITY_MONTH'],
    y=monthly_gp['GP_ENCOUNTERS'],
    name='GP Visits/Appointments',
    mode='lines',
    fill='tozeroy', 
    line=dict(color='#6BFEF4', width=2),
    fillcolor='rgba(78, 205, 196, 0.3)'
  ))

  figure_gp1.update_layout(
    title='Monthly GP Consultation Volume',
    xaxis_title='Month',
    yaxis_title='Number of GP Visits',
    hovermode='x unified',
    height=400
  )

  st.plotly_chart(figure_gp1, width="stretch", key="figure_gp1")

  # Chart 2: GP Visits Compared To Hospital Admissions
  st.subheader("GP Visits Compared To Hospital Admissions")

  #Preparing the Data
  gp_vs_hospital = df_activity.groupby('ACTIVITY_MONTH').agg({
    'GP_ENCOUNTERS': 'sum',
    'IP_ENCOUNTERS': 'sum'
  }).reset_index()

  # Create dual axis chart
  from plotly.subplots import make_subplots

  figure_gp2 = make_subplots(specs=[[{"secondary_y": True}]])

  # Add GP Visits/Appointments (visible on Y axis in graph)
  figure_gp2.add_trace(
    go.Bar(
      x=gp_vs_hospital['ACTIVITY_MONTH'],
      y=gp_vs_hospital['GP_ENCOUNTERS'],
      name='GP Visits',
      marker_color="#CD4EBA"
    ),
    secondary_y=False
  )

  # Add hospital admissions (secondary y-axis)
  figure_gp2.add_trace(
    go.Scatter(
      x=gp_vs_hospital['ACTIVITY_MONTH'],
      y=gp_vs_hospital['IP_ENCOUNTERS'],
      name='Hospital Admissions',
      mode='lines+markers',
      line=dict(color="#6BFF75", width=3),
      marker=dict(size=8)
    ),
    secondary_y=True
  )

  # Update axes
  figure_gp2.update_xaxes(title_text="Month")
  figure_gp2.update_yaxes(title_text="GP Visits", secondary_y=False)
  figure_gp2.update_yaxes(title_text="Hospital Admission", secondary_y=True)

  figure_gp2.update_layout(
    title='GP Activity vs Hospital Admissions',
    hovermode='x unified',
    height=400
  )

  st.plotly_chart(figure_gp2, width="stretch", key="figure_gp2")

  #Chart 3: Patient Visit Frequency Distribution
  st.subheader("Patient Visit Frequency Distribution")

  # Calculate total visits for each paatient
  patient_gp_visits = df_activity.groupby('SK_PATIENT_ID')['GP_ENCOUNTERS'].sum().reset_index()
  patient_gp_visits.columns = ['Patient_ID', 'Total_GP_Visits']

  # Creating the histogram
  figure_gp3 = px.histogram(
    patient_gp_visits,
    x='Total_GP_Visits',
    nbins=20,
    title='Distribution of GP Visits for Each Patient Over 12 Month/Year Period',
    labels={'Total_GP_Visits': 'Total GP Visits', 'count': 'Number of Patients'},
    color_discrete_sequence=["#CD4E9E"]
  ) 

  figure_gp3.update_layout(
    xaxis_title='Total GP Visits Per Each Patient',
    yaxis_title='Number of Patients',
    height=400,
    showlegend=False
  )

  st.plotly_chart(figure_gp3, width="stretch", key="figure_gp3")

  # Chart 4: Average GP Consultation Duration Trends
  st.subheader("Average GP Consultation Duraation Trend")

  # Calculate average duration for each month
  monthly_duration = df_activity.groupby('ACTIVITY_MONTH').apply(
    lambda x: x['GP_DURATION'].sum() / x['GP_ENCOUNTERS'].sum() if x['GP_ENCOUNTERS'].sum() > 0 else 0
  ).reset_index()
  monthly_duration.columns = ['ACTIVITY_MONTH', 'Avg_Duration']

  # Create the line chart
  figure_gp4 = go.Figure()

  figure_gp4.add_trace(go.Scatter(
    x=monthly_duration['ACTIVITY_MONTH'],
    y=monthly_duration['Avg_Duration'],
    mode='lines+markers',
    line=dict(color="#390DB1", width=3),
    marker=dict(size=10, color="#4ECD78"),
    name='Avg Duration'
  ))

  figure_gp4.update_layout(
    title='Average GP Consultation/Appointment Duration Over 12 Month/Year Period',
    xaxis_title='Month',
    yaxis_title='Average appointment Duration (In Minutes)',
    hovermode='x unified',
    height=400
  )

  st.plotly_chart(figure_gp4, width="stretch", key="figure_gp4")

  # Chart 5: GP Activity by Age Ranges/Band
  st.subheader("GP Activity by Age Bands/Ranges")
  
  # Converting Patient ID to String Format for Compatibility
  df_activity["SK_PATIENT_ID_STR"] = "P" + df_activity["SK_PATIENT_ID"].astype("string")

  # Merging with Person data to get the age ranges
  df_gp_age = pd.merge(
    df_activity,
    df_person[['PERSON_ID', 'ANALYSIS_MONTH', 'AGE_BAND_NHS']],
    left_on=['SK_PATIENT_ID_STR', 'ACTIVITY_MONTH'],
    right_on=['PERSON_ID', 'ANALYSIS_MONTH'],
    how='left'
  )

  # Calculate Average GP Visits/Appointments by Each Age Bands/Range
  gp_by_age = df_gp_age.groupby('AGE_BAND_NHS')['GP_ENCOUNTERS'].mean().reset_index()
  gp_by_age.columns = ['Age_Band', 'Avg_GP_Encounters']

  # Sorting by Age Categories
  age_order = ['18-39', '40-64', '65+']
  gp_by_age['Age_Band'] = pd.Categorical(gp_by_age['Age_Band'], categories=age_order, ordered=True)
  gp_by_age = gp_by_age.sort_values('Age_Band')

  # Creating the Bar Chart
  figure_gp5 = px.bar(
    gp_by_age,
    x='Age_Band',
    y='Avg_GP_Encounters',
    title='Average GP Visits/Appointments by Each Age Group',
    labels={'Age_Band': 'Age Band', 'Avg_GP_Encounters': 'Average GP Visits/Appointments Per Month'},
    color='Avg_GP_Encounters',
    color_continuous_scale='Blues',
    text='Avg_GP_Encounters'
  )

  figure_gp5.update_traces(
    texttemplate='%{text:.1f}', # Query this line
    textposition='outside'
  )

  figure_gp5.update_layout(
    showlegend=False,
    height=400
  )

  st.plotly_chart(figure_gp5, width="stretch", key="figure_gp5")

  # Chart 6: GP Visits VS Patient's Existing Conditions
  st.subheader("GP Visits/Appointments Vs Number of Existing Conditions")

# Creating the string version
if "SK_PATIENT_ID_STR" not in df_activity.columns:
  df_activity["SK_PATIENT_ID_STR"] = "P" + df_activity["SK_PATIENT_ID"].astype("string")

  # Merge with Person Data for Existing Conditions
  df_gp_condition = pd.merge(
    df_activity,
    df_person[['PERSON_ID', 'ANALYSIS_MONTH', 'TOTAL_ACTIVE_CONDITIONS']],
    left_on=['SK_PATIENT_ID', 'ACTIVITY_MONTH'],
    right_on=['PERSON_ID', 'ANALYSIS_MONTH'],
    how='left'
)

  # Calculating Average GP Visits/Appointments and Total Cost By Each Patient
  gp_condition_summary = df_gp_condition.groupby('SK_PATIENT_ID').agg({
    'GP_ENCOUNTERS': 'mean',
    'TOTAL_ACTIVE_CONDITIONS': 'mean',
    'TOTAL_COST': 'sum'
    }).reset_index()


# Creating the scatter plot
  figure_gp6 = px.scatter(
    gp_condition_summary,
    x='TOTAL_ACTIVE_CONDITIONS',
    y='GP_ENCOUNTERS',
    size='TOTAL_COST',
    color='TOTAL_COST',
    title='GP Visits Vs Patient Existing Conditions',
    labels={
      'TOTAL_ACTIVE_CONDITIONS': 'Number of Active Health Conditions',
      'GP_ENCOUNTERS': 'Average GP Visits/Appointments For Each Month',
      'Total_COST': 'Total Cost (£)'
    },
    color_continuous_scale='Blues',
    size_max=30
  )


  figure_gp6.update_layout(
    height=450,
    hovermode='closest'
  )

  st.plotly_chart(figure_gp6, width="stretch", key="figure_gp6")

# Main insights for GP Activity Section
  st.markdown("---")
  st.subheader(" Key Insights For GP'S")

  col1, col2 = st.columns(2)

  with col1: 
    peak_month = monthly_gp.loc[monthly_gp['GP_ENCOUNTERS'].idxmax(), 'ACTIVITY_MONTH'].strftime('%B %Y') #Query this line
    lowest_month = monthly_gp.loc[monthly_gp['GP_ENCOUNTERS'].idxmin(), 'ACTIVITY_MONTH'].strftime('%B %Y')
  
  st.info(f"""
  **GP Utilisation Patterns:**
  - Total GP Visits/Appointments in 12 Months/Year Period: {total_gp:,}
  - Average per patient: {avg_per_patient:.1f} visits
  - Peak month: {peak_month} ({monthly_gp['GP_ENCOUNTERS'].max():.0f} visits)
  - lowest month: {lowest_month} ({monthly_gp['GP_ENCOUNTERS'].min():.0f} visits)
  """)
  
  with col2:
  # Calculating the relation between GP Visits and the hospital admissions
    relation = gp_vs_hospital[['GP_ENCOUNTERS', 'IP_ENCOUNTERS']].corr().iloc[0,1]
  
  st.info(f"""
  **Relation Between GP and Hospital**
  - Average consultation/appointment time: {avg_consultation:.1f} minutes
  - Relation with admissions: {relation:.2f}
  - Heavy utilizers (>10 appointments/month): {len(high_utilizers)} patients
  - {'Negative relation could imply GP Visits/Appointments might reduce admissions' if relation < 0 else 'Positive relation suggests that more unwell/sicker patients see their GP more'}
  """)

    
# Section 3: Community Provider Activity
elif section == "Community provider activity":
  st.header("Community Provider Activity")
  
  # Metrics row for the community care provider section
  st.subheader("Vital Community Care Provider Metrics")
  
  # Creating the 5 columns for each metric in community care provider metrics
  col1, col2, col3, col4, col5 = st.columns(5)
  
  with col1: 
    total_cc = int(df_activity['CC_ENCOUNTERS'].sum())
    st.metric(
      label="Total Community Care Contacts",
      value=f"{total_cc:,}"
    )
    
  with col2: 
    avg_cc_per_patient = df_activity.groupby('SK_PATIENT_ID')['CC_ENCOUNTERS'].sum().mean()
    st.metric(
      label="Average Number of Community Care Contacts Per Each Patient",
      value=f"{avg_cc_per_patient:.1f}"
    )
    
  with col3:
    total_cc_duration = df_activity['CC_DURATION'].sum()
    total_cc_hours = total_cc_duration / 60 # Converting the minutes to hours for simplicity
    st.metric(
      label="The Total Number of Community Care Provider Hours Utilised"
      value=f"{total_cc_hours:,.0f} hours"
    )
    
  with col4: 
    total_cc_cost = df_activity['CC_COST'].sum()
    st.metric(
      label="The Total Community Care Cost",
      value=f"£{total_cc_cost:,.0f}"
    )
  
  with col5: 
    patients_receiving_communitycare = df_activity[df_activity['CC_ENCOUNTERS'] > 0]['SK_PATIENT_ID'].nunique() # Query this line and explain it
    total_patients = df_activity['SK_PATIENT_ID'].nunique()
    pct_receiving_communitycare = (patients_receiving_communitycare / total_patients * 100) if total_patients > 0 else 0
    st.metric(
      label="% Of Patients Receiving Community Care",
      value=f"{pct_receiving_communitycare:.1f}%"
    )
    
  st.markdown("---") # Query this line and explain it
  
  # Visualisations of Communiy Care Providers
  st.header("Analysis of Community Care Activity")
  
  # Chart 1: Volume of community care over the year/12 month period
  st.subheader("Volume of Community Care Over The Year/12 Month Period")
  
  # Data preperation
  monthly_cc = df_activity.groupby('ACTIVITY_MONTH').agg({
    'CC_ENCOUNTERS': 'sum'
  }).reset_index()
  
  # Creating the line chart with fill to see results
  figure_cc1 = go.Figure()
  
  figure_cc1.add_trace(go.Scatter(
    x=monthly_cc['ACTIVITY_MONTH'],
    y=monthly_cc['CC_ENCOUNTERS'],
    name='Community Care Contacts',
    mode='lines',
    fill='tozeroy',
    line=dict(color="#0C3BCA", width=2),
    fillcolor='rgba(155, 89, 182, 0.3)' # Explain and query this line for the RGBA and numbers
  ))
  
  figure_cc1.update_layout(
    title='Number of Monthly Community Care visits and Contacts',
    xaxis_title='Number of Community Care Contacts and Visits',
    yaxis_title='Number of Community Care Contacts and Visits',
    hovermode='x unified', # Query hovermode, what it is and why we need it
    height=400
  )
  
  st.plotly_chart(figure_cc1, width="stretch", key="figure_cc1")
  
  # Chart 2: Mix of Care Settings with GP, Hospital and Community Care Provider
  st.subheader("Mix of Care Settings Over The Year/12 Month Period")
  
  # Prepping the Data to be added
  mix_of_care = df_activity.groupby('ACTIVITY_MONTH').agg({
    'GP_ENCOUNTERS': 'sum',
    'CC_ENCOUNTERS': 'sum',
    'OP_ENCOUNTERS': 'sum',
    'IP_ENCOUNTERS': 'sum',
    'AE_ENCOUNTERS': 'sum'
  }).reset_index()
  
  # Creating the Stacked Chart
  figure_cc2 = go.Figure()
  
  figure_cc2.add_trace(go.Scatter(
    x=mix_of_care['ACTIVITY_MONTH'],
    y=mix_of_care['GP_ENCOUNTERS'],
    name='GP',
    mode='lines',
    stackgroup='one',
    fillcolor="#19DD9C"
  ))
  
  figure_cc2.add_trace(go.Scatter(
    x=mix_of_care['ACTIVITY_MONTH'],
    y=mix_of_care['CC_ENCOUNTERS'],
    name='Community Care Provider',
    mode='lines',
    stackgroup='one',
    fillcolor="#52E90C"
  ))
  
  figure_cc2.add_trace(go.Scatter(
    x=mix_of_care['ACTIVITY_MONTH'],
    y=mix_of_care['OP_ENCOUNTERS'],
    name='Outpatients',
    mode='lines',
    stackgroup='one',
    fillcolor="#CBA930"
  ))
  
  figure_cc2.add_trace(go.Scatter(
    x=mix_of_care['ACTIVITY_MONTH'],
    y=mix_of_care['IP_ENCOUNTERS'],
    name='Inpatients',
    mode='lines',
    stackgroup='one',
    fillcolor="#E11010"
  ))
  
  figure_cc2.add_trace(go.Scatter(
    x=mix_of_care['ACTIVITY_MONTH'],
    y=mix_of_care['AE_ENCOUNTERS'],
    name='A&E',
    mode='lines', 
    stackgroup='one',
    fillcolor="#6C0A8A"
  ))
  
  figure_cc2.update_layout(
    title='Mix of Care Settings Across All The Various Service Types Used For Heart Failure',
    xaxis_title='Month',
    yaxis_title='Number of Encounters Across All Health Services Used',
    hovermode='x unified',
    height=400
  )
  
  st.plotly_chart(figure_cc2, width="stretch", key="figure_cc2")
  
  # Chart 3: Community Care Utilisation for Area Deprivation
  st.subheader("Community Care Utilisation by Deprivation Level in Areas")
  
  # Convert Patient ID to String format for compatibility
  df_activity["SK_PATIENT_ID_STR"] = "P" + df_activity["SK_PATIENT_ID"].astype("string")
  
  # Merging with Person Data to see and get the deprivation levels
  df_cc_imd = pd.merge(
    df_activity,
    df_person[['PERSON_ID', 'ANALYSIS_MONTH', 'IMD_QUINTILE_19']],
    left_on=['SK_PATIENT_ID_STR', 'ACTIVITY_MONTH'],
    right_on=['PERSON_ID', 'ANALYSIS_MONTH'],
    how='left'
  )
  
  # Calculating the Average Community Care Utilisation Using Deprivation
  cc_by_imd = df_cc_imd.groupby('IMD_QUINTILE_19')['CC_ENCOUNTERS'].mean().reset_index()
  cc_by_imd.columns = ['IMD_Quintile', 'Avg_CC_Encounters']
  
  # Sorting and arranging using Quintile range (1 being most deprived, and 5 being least deprived)
  cc_by_imd = cc_by_imd.sort_values('IMD_Quintile')
  
  # Create bar chart
  figure_cc3 = px.bar(
    cc_by_imd,
    x='IMD_Quintile',
    y='Avg_CC_Encounters',
    title='The Average Community Care Contacts and Visits From Patients By Deprivation Level Across Areas',
    labels={
      'IMD_Quintile': 'IMD Quintile (1=Most Deprived Level, 5=Least Deprived Level)',
      'Avg_CC_Encounters': 'Average Community Care Contacts and Visits Per Month by Patients'
    },
    color='Avg_CC_Encounters',
    color_continuous_scale='Purple',
    text='Avg_CC_Encounters'
  )
  
  figure_cc3.update_traces(
    texttemplate='%{text:.2f}',
    textposition='outside'
  )
  
  figure_cc3.update_layout(
    showlegend=False,
    height=400
  )
  
  st.plotly_chart(figure_cc3, width="stretch", key="figure_cc3")
  
  # Chart 4: Community Care Specifically Using Frailty Status
  st.subheader("Community Care Specifically Using Frailty Status")
  
  # Merging with Person Data to Get and See Frailty Status within Patients
  df_cc_frail = pd.merge(
    df_activity,
    df_person[['PERSON_ID', 'ANALYSIS_MONTH', 'HAS_FRAIL']],
    left_on=['SK_PATIENT_ID_STR', 'ACTIVITY_MONTH'],
    right_on=['PERSON_ID', 'ANALYSIS_MONTH'],
    how='left'
  )
  
  # Calculating The Average Community Care Contacts/Visits by Frailty
  cc_by_frailty = df_cc_frail.groupby('HAS_FRAIL')['CC_ENCOUNTERS'].mean().reset_index()
  cc_by_frailty.columns = ['Frailty_Status', 'Avg_CC_Encounters']
  
  # Replacing the Boolean labels with suitable readable labels
  cc_by_frailty['Frailty_Status'] = cc_by_frailty['Frailty_Status'].map({
    True: 'Frail',
    False: 'Not Frail'
  })
  
  # Creating a Grouped Bar Chart to Display The Data
  figure_cc4 = px.bar(
    cc_by_frailty,
    x='Frailty_Status',
    y='Avg_cc_Encounters',
    title='The Average Community Care Visits/Contacts Based On Frailty Status',
    labels={
      'Frailty_Status': 'Frailty Status',
      'Avg_CC_Encounters': 'The Average Community Care Visits/Contacts Per Each Month'
    },
    color='Frailty_Status',
    color_discrete_map={'Frail': "#A70505", 'Not Frail': "#7D4904"},
    text='Avg_CC_Encounters'
  )
  
  figure_cc4.update_traces(
    texttemplate='%{text:.2f}',
    textposition='outside'
  )
  
  figure_cc4.update_layout(
    showlegend=False,
    height=400
  )
  
  st.plotly_chart(figure_cc4, width="stretch", key="figure_cc4")
  
  # Chart 5: Community Care Visit Length in Minutes Consistency (Box Plot)
  st.subheader("Community Care Visit Length in Minutes Consistency")
  
  # Prepping the data - getting the durations where the visits/contacts are listed
  cc_duration_data = []
  
  for idx, row in df_activity.iterrows():
    if row['CC_ENCOUNTERS'] > 0 and row['CC_DURATION'] > 0:
      avg_duration = row['CC_DURATION'] / row['CC_ENCOUNTERS']
      month_str = row['ACTIVITY_MONTH'].strftime('%b %Y')
      cc_duration_data.append({
        'Month': month_str,
        'Avg_Duration': avg_duration
      })
      
  cc_duration_df = pd.DataFrame(cc_duration_data)
  
  # Creating the box plot for chart 5
  if not cc_duration_df.empty:
    figure_cc5 = px.box(
      cc_duration_df,
      x='Month',
      y='Average_Duration',
      title='Community Care Visit/Contact Duration for Each Month',
      labels={
        'Month': 'Month',
        'Average_Duration': 'The Average Duration of Visit/Contact (Minutes)' 
      },
      color_discrete_sequence=["#7F5490"]
    )
    
    figure_cc5.update_layout(
      showlegebd=False,
      height=400,
      xaxis_tickangle=-45
    )
    
    st.plotly_chart(figure_cc5, width="stretch", key="figure_cc5")
  else:
    st.info("No Community Care Visit/Contact Duration Data Available for This Period.")
    
    
  # Chart 6: Shows the mix of care settings that the top 20 patients use in percentage breakdown (Using Stacked Bar Graph) *Query this explanation*
  st.subheader("Shows The Mix of Care Settings That The Top 20 Patients Use in As a Percentage Breakdown Using a Stacked Bar Graph")
  
  # Calculating the Total Number of Encounters by Each Patient and the Care Setting
  patient_care_mix = df_activity.groupby('S_PATIENT_ID').agg({
    'GP_ENCOUNTERS': 'sum',
    'CC_ENCOUNTERS': 'sum',
    'OP_eENCOUNTERS': 'sum',
    'IP_ENCOUNTERS': 'sum',
    'AE_ENCOUNTERS': 'sum'
  }).reset_index()
  
  # Calculating the total number of encounters per each patient
  patient_care_mix['Total_Encounters'] = patient_care_mix[
    ['GP_ENCOUNTERS', 'CC_ENCOUNTERS, 'OP_ENCOUNTERS', 'IP_ENCOUNTERS', 'AE_ENCOUNTERS']
  ].sum(axis=1)
  
  # Getting the top 20 Patients By The Total Encounters
 top_20_patients = patient_care_mix.nlargest(20, 'Total_Encounters')
 
 # Calculating the percentages for each care setting
 top_20_patients['GP_%'] = (top_20_patients['GP_ENCOUNTERS'] / top_20_patients['Total_Encounters'] * 100)
 top_20_patients['CC_%'] = (top_20_patients['CC_ENCOUNTERS'] / top_20_patients['Total_Encounters'] * 100)
 top_20_patients['OP_%'] = (top_20_patients['OP_ENCOUNTERS'] / top_20_patients['Total_Encounters'] * 100)
 top_20_patients['IP_%'] = (top_20_patients['IP_ENCOUNTERS'] / top_20_patients['Total_Encounters'] * 100) 
 top_20_patients['AE_%'] = (top_20_patients['AE_ENCOUNTERS'] / top_20_patients['Total_Encounters'] * 100)
 
 # Creating the stacked bar chart
 figure_cc6 = go.Figure()
 
 figure_cc6.add_trace(go.Bar(
   x=yop_20_patients['SK_PATIENT_ID'],
   y=top_20_patients['GP_%'],
   name='GP',
   marker_color='#3498DB'
 ))
  
  figure_cc6.add_trace(go.Bar(
    x=top_20_patients['SK_PATIENT_ID'],
    y=top_20_patients['CC_%'],
    name='Community Care',
    marker_color='#9B59B6'
  ))
  
  figure_cc6.add_trace(go.bar(
    x=top_20_patients['SK_PATIENT_ID'],
    y=top_20_patients['OP_%'],
    name='Outpatients',
    marker_color='#2ECC71'
  ))
  
  figure_cc6.add_trace(go.Bar(
    x=top_20_patients['SK_PATIENT_ID'],
    y=top_20_patients['IP_%'],
    name='Inpatients',
    marker_color='#E74C3C'
  ))
  
  figure_cc6.add_trace(go.Bar(
    x=top_20_patients['SK_PATIENT_ID'],
    y=top_20_patients['AE_%'],
    name='A&E',
    marker_color='#f39C12'
  ))
  
  figure_cc.update_layout(
    bar,mode='stack',
    title='Mix of Care Settings For the Top 20 Highest Workforce Utilising Patients',
    xaxis_title='Patient ID',
    yaxis_title='Percentage of The Total Workforce Encounters %',
    hovermode='x unified',
    height=450
  )
  
  st.plotly_chart(figure_cc6, width="stretch", key="figure_cc6")
  
  # Key summaries relavent for the Community Care Provider Section
  st.markdown("---")
  st.subheader(" Key Summaries for the Community Care Provider")
  
  col1, col2 = st.columns(2)
  
  with col1: 
    peak_cc_month = monthly_cc.loc[monthly_cc]