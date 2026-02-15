import pandas as pd # pandas is a data manipulation and analysis library.
import numpy as np # numpy is for multidimensional array manipulation.
import streamlit as st #installing streamlit as st. Streamlit is for hosting the dashboard.

#setting the Dashboard Title.
st.title("Heart Failure Workforce Utilisation Tool")

# Loading my dashboard data
def loadData():
    df_person=pd.read_excel ('/content/Heart_Failure_Patient_Data_12_Months_20_Patients.xlsx', sheet_name ='PERSON_MONTH_DATA') # df - data frame, pd - pandas object. read_excel allows me to open and read the data in my excel spreadsheet and use it in the code.
    df_person # Data frame is a data structure for storing tabular data in Python.
    print (df_person)
    # The difference between df and print(df) is df is evaluating the object, i.e. it is displaying it in a pretty table format, whereas print(df) is printing it as text.

    df_activity=pd.read_excel ('/content/Heart_Failure_Patient_Data_12_Months_20_Patients.xlsx', sheet_name ='FCT_ACTIVITY_DATA') # loading the activity data for the dashboard.
    print(df_activity)
    
    df_activity_catalogue=pd.read_excel ('/content/Heart_Failure_Patient_Data_12_Months_20_Patients.xlsx', sheet_name ='FCT_ACTIVITY_CATALOGUE') # loading the activity catalogue data for the dashboard.
    print(df_activity_catalogue)
    
    df_person_month_catalogue=pd.read_excel ('/content/Heart_Failure_Patient_Data_12_Months_20_Patients.xlsx', sheet_name ='PERSON_MONTH_CATALOGUE') # loading the person month catalogue data for the dashboard.
    print(df_person_month_catalogue)
    
    df_person, df_activity = loadData()
    st.success(f"Loaded {len(df_person)} person records and {len(df_activity)} activity records")
    
# Adding navigational sidebar on dashboard
st.sidebar.title("Dashboards")

section = st.sidebar.radio(
  
  "Select a Section: ", 
  [
    "Hospital operations", 
    "Patient outcomes", 
    "Healthcare costs"
  ]
)

st.sidebar.markdown("---")
    
# Displaying the contents of each section of the dashboard
if section == ("Hospital operations"):
  st.header("Hospital operations")
  st.write("Hospital operations contents will be displayed here")
  # Showing sample data from my Excel spreadsheet
  # st.dataframe(df_activity.head())
  
elif section == "Patient outcomes": 
  st.header("Patient outcomes")
  st.write("Patient outcomes contents will be displayed here")
  # Showing some sample data from my Excel spreadsheet
  #st.dataframe(df_person.head())
  
elif section == "Heathcare costs":
  st.header("Healthcare costs")
  st.write("Healthcare costs contents will be displayed here")
  df_person, df_activity, df_activity_catalogue, df_person_month_catalogue = loadData()
  #Showing some sample data from my Excel spreadsheet
  st.metric("Total cost", f"£{df_activity['total cost'].sum():,.2f}") 
  