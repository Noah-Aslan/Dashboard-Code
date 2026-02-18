import pandas as pd # pandas is a data manipulation and analysis library.
import numpy as np # numpy is for multidimensional array manipulation.
import streamlit as st #installing streamlit as st. Streamlit is for hosting the dashboard.

# setting the page configuration
st.set_page_config(
  page_title="Heart Failure Workforce Utilisation Tool",
  layout="wide"
)

# Initialisation of session state for navigation
if 'current_page'not in st.session_state:
  st.session_state.current_page = "Hospital activity"

# Loading my dashboard data
def loadData():
    df_person=pd.read_excel ('Heart_Failure_Patient_Data_12_Months_20_Patients.xlsx', sheet_name ='PERSON_MONTH_DATA') # df - data frame, pd - pandas object. read_excel allows me to open and read the data in my excel spreadsheet and use it in the code.
    df_person # Data frame is a data structure for storing tabular data in Python.
    print (df_person)
    # The difference between df and print(df) is df is evaluating the object, i.e. it is displaying it in a pretty table format, whereas print(df) is printing it as text.

    df_activity=pd.read_excel ('Heart_Failure_Patient_Data_12_Months_20_Patients.xlsx', sheet_name ='FCT_ACTIVITY_DATA') # loading the activity data for the dashboard.
    print(df_activity)
    
    df_activity_catalogue=pd.read_excel ('Heart_Failure_Patient_Data_12_Months_20_Patients.xlsx', sheet_name ='FCT_ACTIVITY_CATALOGUE') # loading the activity catalogue data for the dashboard.
    print(df_activity_catalogue)
    
    df_person_month_catalogue=pd.read_excel ('Heart_Failure_Patient_Data_12_Months_20_Patients.xlsx', sheet_name ='PERSON_MONTH_CATALOGUE') # loading the person month catalogue data for the dashboard.
    print(df_person_month_catalogue)
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


  
  # Showing sample data from my Excel spreadsheet
  # st.dataframe(df_activity.head())
  
elif section == "GP activity": 
  st.header("GP activity")
  st.write("GP activity contents will be displayed here")
  # Showing some sample data from my Excel spreadsheet
  #st.dataframe(df_person.head())
  
elif section == "Community provider activity":
  st.header("Community provider activity")
  st.write("Community provider activity contents will be displayed here")
  # df_person, df_activity, df_activity_catalogue, df_person_month_catalogue = loadData()
  # Showing some sample data from my Excel spreadsheet
  # st.metric("Total cost", f"£{df_activity['total cost'].sum():,.2f}") 
  
# Displaying the contents of each section of the dashboard

  
    