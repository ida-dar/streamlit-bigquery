# import json

import streamlit as st
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
from streamlit_option_menu import option_menu

# VARIABLES
page_title = 'BigQuery Public Databases'
layout = 'wide'

# DROPDOWN VALUES
publicDatabases = [ 'gsod', 'github_nested', 'github_timeline', 'natality', 'shakespeare', 'trigrams', 'wikipedia' ]

# HEADERS
selectDB = 'Select a database'
dbVisualization = 'Database Visualization'

# PAGE CONFIGURATION
st.set_page_config( page_title=page_title, layout=layout )
st.title( page_title )
st.subheader('Please note all searches are limited to 50 results')

# NAVIGATION
selected = option_menu(
  menu_title=None,
  options=[ selectDB, dbVisualization ],
  icons=[ 'pencil-fill', 'bar-chart-fill' ],  # https://icons.getbootstrap.com/
  orientation='horizontal',
)

# Create API client
credentials = service_account.Credentials.from_service_account_info(
  st.secrets['gcp-service-account']
)
# Another option for reading credentials if json file is present. Left for future reference
# credentials = service_account.Credentials.from_service_account_info(
#   json.load( open( 'service-account.json' ) )
# )

client = bigquery.Client( credentials=credentials )


# Perform query
# Uses st.experimental_memo to only rerun when the query changes or after 10 min
@st.experimental_memo( ttl=600 )
def run_query( query ):
  query_job = client.query( query )
  rows_raw = query_job.result()
  # Convert to list of dicts. Required for st.experimental_memo to hash the return value.
  rows = [ dict( row ) for row in rows_raw ]
  return rows


# HIDE STREAMLIT DEFAULT STYLE
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown( hide_st_style, unsafe_allow_html=True )

# DATABASES VALUES
if selected == selectDB:
  with st.form( 'db_from' ):
    st.selectbox( 'Select Public Database', publicDatabases, key='publicDatabases' )

    '---'
    submitted = st.form_submit_button( 'Save' )
    if submitted:
      dbs = str( st.session_state[ 'publicDatabases' ] )
      st.success( f'Successfully saved data for {dbs}' )

if selected == dbVisualization:
  dbs = str( st.session_state[ 'publicDatabases' ] )
  rows = run_query(
    f"SELECT * FROM `bigquery-public-data.samples.{dbs}` LIMIT 50" )

  # Print results
  df = pd.DataFrame( rows )
  st.table( df )
