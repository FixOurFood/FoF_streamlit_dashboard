import streamlit as st
import gspread
from google.oauth2 import service_account

SCOPES = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = dict(st.secrets["gspread"]["gs_api_key"])

credentials = service_account.Credentials.from_service_account_info(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

gc = gspread.authorize(credentials)
sh = gc.open_by_key("1ZEb7PzEi6aKv303t7ypFriIt89FPzXTySGt_vmY60_Y")
ws = sh.worksheet("Stage I submissions")

stage_I_deadline = 'December 31, 2024'

def submit_scenario(user_id, ambition_levels=False):
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
        ws.append_row(row)
        return
    
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
    ]

    ws.append_row(row)

if __name__ == "__main__":
    submit_scenario("TEST")