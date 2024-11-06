import streamlit as st
import gspread
from google.oauth2 import service_account
from utils.helper_functions import update_slider, reset_sliders

SCOPES = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = dict(st.secrets["gspread"]["gs_api_key"])

credentials = service_account.Credentials.from_service_account_info(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

gc = gspread.authorize(credentials)
sh = gc.open_by_key("1ZEb7PzEi6aKv303t7ypFriIt89FPzXTySGt_vmY60_Y")
stage_I_worksheet = sh.worksheet("Stage I submissions")
pathways_worksheet = sh.worksheet("AFN Scenarios pass 1")
enrolments_worksheet = sh.worksheet("Form responses 2")

stage_I_deadline = 'December 31, 2024'

def get_user_list():
    """Get the list of user IDs from the Google Sheet"""

    user_list = enrolments_worksheet.col_values(5)
    user_list = user_list[1:]
    return user_list

@st.dialog("Submit scenario")
def submit_scenario(user_id, SSR, total_emissions, ambition_levels=False):
    """Submit the pathway to the Google Sheet.

    Parameters:
    ----------

    user_id : str
        The user's ID.
        
    ambition_levels : bool
        Whether to submit the ambition levels stored in the session state, or
        run a test submission with dummy data instead.

    Returns:
    -------
        None
    """

    if not ambition_levels:
        row = [user_id, "test"]
        stage_I_worksheet.append_row(row)
        return
    
    if user_id not in get_user_list():
        st.error(f'User ID {user_id} not found in database', icon="🚨")
    
    else:
        row = [user_id,
            st.session_state["ruminant"],
            st.session_state["dairy"],
            st.session_state["pig_poultry_eggs"],
            st.session_state["fruit_veg"],
            st.session_state["cereals"],
            st.session_state["waste"],
            st.session_state["labmeat"],
            
            st.session_state["pasture_sparing"],
            st.session_state["arable_sparing"],
            st.session_state["land_beccs"],
            st.session_state["foresting_spared"],

            st.session_state["silvopasture"],
            st.session_state["methane_inhibitor"],
            st.session_state["manure_management"],
            st.session_state["animal_breeding"],
            st.session_state["fossil_livestock"],

            st.session_state["agroforestry"],
            st.session_state["fossil_arable"],

            st.session_state["waste_BECCS"],
            st.session_state["overseas_BECCS"],
            st.session_state["DACCS"],
            
            '{0:.2f}'.format(SSR),
            '{0:.2f}'.format(total_emissions)
        ]

        stage_I_worksheet.append_row(row)
        st.success(f'Scenario submitted for user {user_id}', icon="✅")

def get_pathways():
    """Get the pathways names from the Google Sheet"""

    values = pathways_worksheet.col_values(1)
    return values[2:]

def get_pathway_data(pathway_name):
    """Get the scenario data from the Google Sheet"""

    values = pathways_worksheet.col_values(1)
    idx = values.index(pathway_name)

    pathway_values = pathways_worksheet.row_values(idx + 1)
    pathway_values = pathway_values[1:]

    # Convert string values to numbers, replacing "no value" with 0
    pathway_values = [float(x) if x != "Float" and x != "" else 0 for x in pathway_values]
    
    return pathway_values

def call_scenarios():
    """Call the scenarios from the Google Sheet"""
        # reset all states
    reset_sliders()
    # get scenario state
    scenario = st.session_state["scenario"]
    pathway_data = get_pathway_data(scenario)

    keys=[
        "ruminant",
        "dairy",
        "pig_poultry_eggs",
        "fruit_veg",
        "cereals",
        "waste",
        "labmeat",

        "pasture_sparing",
        "arable_sparing",
        "land_beccs",
        "foresting_spared",
        
        "silvopasture",
        "methane_inhibitor",
        "manure_management",
        "animal_breeding",
        "fossil_livestock",
        
        "agroforestry",
        "fossil_arable",
        
        "waste_BECCS",
        "overseas_BECCS",
        "DACCS",
    ]

    update_slider(keys, pathway_data)


if __name__ == "__main__":
    # submit_scenario("TEST")

    pathway_names = get_pathways()
    print(get_pathway_data(pathway_names[0]))

    print(get_user_list())