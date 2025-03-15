import streamlit as st
import requests
import time
import pandas as pd


def get_data(api_key, sheet_name):
    # Fetch data from the Google Apps Script API using the specified sheet name
    url = f'https://script.google.com/macros/s/{api_key}/exec?sheet={sheet_name}'
    response = requests.get(url)  # Send a GET request to the API
    return response

def generate_substrings(long_string, depth):
    return [long_string[i:i+depth] for i in range(len(long_string) - depth + 1)]

def count_overlay_items(substrings, target_string):
    overlay_items = sum(1 for substr in substrings if substr in target_string)
    overlay_percentage = round(overlay_items / len(substrings) * 100, 4)
    return overlay_items, overlay_percentage


def mainloop(api_key):
    # Dropdown menu options
    sheet_names = ["Choose from below:",
                   "sheet_sdca",
                   "sheet_ltpi",
                   "sheet_mtpi",
                   "sheet_rsps",
                   "code_btc",
                   "code_eth",
                   "code_alt",
                   "sheet_sops"]

    # Dropdown to select the level
    sheet_name = st.selectbox("Choose Level to Grade", sheet_names, key="selected_option")
    with st.form(key="submission_form"):
        student_uid = st.text_input("Student UID", value="")
        attempt = st.text_input("Attempt", value="")
        depth = st.text_input("Analysis Depth (int)", value="")
        significance_threshold = st.text_input("Threshold of Significance (float: XXX.xx)",value="")
        submit_button = st.form_submit_button("Submit")

        if not (sheet_name == "Choose Level to Grade") and submit_button:

            # Get Data
            start_time_api = time.time()
            api_response = get_data(api_key, sheet_name).json()
            end_time_api = time.time()
            elapsed_time = end_time_api - start_time_api
            st.write("---")
            st.write(f"API time: {elapsed_time:.5f} seconds.")

            # Parse Data
            times = list(api_response["Time"])
            UIDs = list(api_response["UID"])
            strings = list(api_response["String"])

            id = list(range(0, len(times)))

            student_subs = [[], [], [], []]
            for i in id:
                index = i  # Use 'i' directly to avoid searching the list unnecessarily
                if student_uid == UIDs[index]:
                    student_subs[0].append(times[index])
                    student_subs[1].append(UIDs[index])
                    student_subs[2].append(strings[index])

            student_subs[3] = list(range(0, len(student_subs[0])))

            target_string = student_subs[2][int(attempt) - 1]
            target_substrings = generate_substrings(target_string, int(depth))

            student_past_subs = [[], [], [], []]
            list_of_lists = [[], [], [], []]

            # Process
            start_time_ac = time.time()

            # Student previous submissions
            for i in student_subs[3]:
                index = i  # Use 'i' directly
                overlay_items, overlay_percentage = count_overlay_items(target_substrings, student_subs[2][index])
                b_overlay_percentage = "na"

                if overlay_percentage > float(significance_threshold):
                    backward_check = generate_substrings(student_subs[2][index], int(depth))
                    b_overlay_items, b_overlay_percentage = count_overlay_items(backward_check, target_substrings)

                    student_past_subs[0].append(student_subs[0][index])          # timestamps
                    student_past_subs[1].append(student_subs[1][index])           # user IDs
                    student_past_subs[2].append(overlay_percentage)     # forward overlay percentage
                    student_past_subs[3].append(b_overlay_percentage)   # backward overlay percentage

            # Other submissions (excluding current student's submissions)
            for i in id:
                index = i  # Use 'i' directly
                overlay_items, overlay_percentage = count_overlay_items(target_substrings, strings[index])
                b_overlay_percentage = "na"

                if overlay_percentage > float(significance_threshold):
                    backward_check = generate_substrings(strings[index], int(depth))
                    b_overlay_items, b_overlay_percentage = count_overlay_items(backward_check, target_substrings)

                    if not student_uid == UIDs[index]:
                        list_of_lists[0].append(times[index])          # timestamps
                        list_of_lists[1].append(UIDs[index])           # user IDs
                        list_of_lists[2].append(overlay_percentage)     # forward overlay percentage
                        list_of_lists[3].append(b_overlay_percentage)   # backward overlay percentage

            end_time_ac = time.time()
            elapsed_time_ac = end_time_ac - start_time_ac
            st.write(f"Breakdown analysis time for {len(times)} tests: {elapsed_time_ac:.5f} seconds.")

            st.write(f"Breakdown depth: {depth}:")

            # Convert the data into a pandas DataFrame
            df_p = pd.DataFrame({
                "Submitted by": student_past_subs[1],
                "At": student_past_subs[0],
                "1st order overlay (%)": student_past_subs[2],
                "2nd order overlay (%)": student_past_subs[3]
            })

            st.write("Student's previous attempts")
            st.dataframe(df_p, use_container_width=True)

            # Convert the data into a pandas DataFrame
            df = pd.DataFrame({
                "Submitted by": list_of_lists[1],
                "At": list_of_lists[0],
                "1st order overlay (%)": list_of_lists[2],
                "2nd order overlay (%)": list_of_lists[3]
            })
            st.write("All Other submissions with overlay above Threshold of Significance")
            st.dataframe(df, use_container_width=True)
