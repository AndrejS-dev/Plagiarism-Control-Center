import streamlit as st
from security import check_password, check_api_key
from mainloop import mainloop

# Initialize session state
if "password_verified" not in st.session_state:
    st.session_state.password_verified = False

if "api_key_verified" not in st.session_state:
    st.session_state.api_key_verified = False

if "form_submitted" not in st.session_state:
    st.session_state.form_submitted = False

# Callback for password verification
def verify_password():
    password = st.session_state.password_input
    if check_password(password):
        st.session_state.password_verified = True
        st.success("Password verified!")
    else:
        st.error("Invalid password!")

# Callback for API key verification
def verify_api_key():
    api_key = st.session_state.api_key_input
    if check_api_key(api_key):
        st.session_state.api_key_verified = True
        st.session_state.api_key = api_key  # Store the verified API key
        st.success("API key verified!")
    else:
        st.error("Invalid API key! Make sure there are no spaces before or after the API key.")

# Password input section
if not st.session_state.password_verified:
    st.title("Login")
    password = st.text_input("Enter password", type="password", key="password_input")
    st.button("Submit Password", on_click=verify_password)

# API key input section
if st.session_state.password_verified and not st.session_state.api_key_verified:
    st.title("API Key Verification")
    api_key = st.text_input("Enter API key", type="password", key="api_key_input")
    st.button("Submit API Key", on_click=verify_api_key)

# Main form submission section
if st.session_state.password_verified and st.session_state.api_key_verified:
    if "api_key" in st.session_state:
        notes = st.expander("Notes")
        notes.markdown("""
        ### 1. How Plagiarism Check Is Performed
        - The target string is broken down into substrings of a specific length (depth).
        - These substrings are compared against records in the database to identify overlaps.
        - Overlaps are analyzed using forward (1st order) and backward (2nd order) checks.

        ### 2. Depth
        - **Definition**: Depth refers to the length of each substring.
        - Example: For depth = 3, the string "abcde" produces substrings `['abc', 'bcd', 'cde']`.

        ### 3. Significance Threshold
        - **Definition**: The minimum overlap percentage required to include a record in the results.
        - Records with overlay percentages below this threshold are excluded from the output.

        ### 4. 1st Order vs. 2nd Order Overlays
        - **1st Order Overlay**: Percentage of substrings from the target string found in another record.
        - **2nd Order Overlay**: Percentage of substrings from another record found in the target string.
        - Example:
          - Target string substrings: `['abc', 'bcd', 'cde']`.
          - Other record substrings: `['abc', 'bcd', 'xyz', 'xyx']`.
          - **1st Order**: 2/3 = 66.67%.
          - **2nd Order**: 2/4 = 50%.

        ### Additional Information
        - Both overlays are used to provide a two-way comparison.
        - Outputs are filtered using the significance threshold for clarity and relevance.

        """)
        mainloop(st.session_state.api_key)
    else:
        st.error("API key is missing. Please re-enter the API key.")
