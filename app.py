# app.py
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import os

st.set_page_config(page_title="Kitui PWD Dashboard", layout="wide")

# === File Path ===
CSV_FILE = "C:/Users/IZOOH/Desktop/PWD/PWD_Disability_Set.csv"

# === Load CSV Data ===
@st.cache_data
def load_data():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE)
    else:
        return pd.DataFrame(columns=["Name", "Phone", "Disability Type", "Assistive Device", "Sub-County", "Ward"])

df = load_data()
df = df.drop(columns=["Unnamed: 6"], errors="ignore")


# === Admin Login ===
st.sidebar.header("🔐 Admin Login")

# Simple hardcoded password
password = st.sidebar.text_input("Enter admin password", type="password")
is_admin = password == "kitui123"  # ✅ You can change this

# === ADMIN-ONLY FEATURES ===
if is_admin:
    import time
    from datetime import datetime
    import shutil
    import glob

    st.sidebar.success("✅ Logged in as Admin")

    # === Upload Excel/CSV and Merge ===
    st.sidebar.header("📤 Upload New PWD Data")
    uploaded_file = st.sidebar.file_uploader("Upload Excel or CSV file", type=["xlsx", "csv"])

    if uploaded_file:
        try:
            with st.spinner("Reading uploaded file..."):
                time.sleep(1)

                if uploaded_file.name.endswith(".csv"):
                    new_data = pd.read_csv(uploaded_file)
                else:
                    new_data = pd.read_excel(uploaded_file)

            expected_columns = ["Name", "Phone", "Disability Type", "Age", "Assistive Device", "Sub-County", "Ward"]

            if list(new_data.columns) == expected_columns:
                st.subheader("📄 Preview Uploaded Data")
                st.dataframe(new_data)

                action = st.radio("How should we handle the new data?", ["Append to existing", "Replace existing"])

                if st.button("✔ Confirm Import"):
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    backup_path = f"{CSV_FILE.replace('.csv', '')}_backup_{timestamp}.csv"
                    shutil.copy(CSV_FILE, backup_path)
                    st.success(f"📦 Backup saved: {backup_path}")

                    with st.spinner("Saving merged data..."):
                        if action == "Append to existing":
                            df = pd.concat([df, new_data], ignore_index=True).drop_duplicates()
                        else:
                            df = new_data

                        df.to_csv(CSV_FILE, index=False)
                        st.success("✅ Data successfully imported and saved.")
                        st.cache_data.clear()
                        st.rerun()
            else:
                st.error("❌ Uploaded file has incorrect columns.")
                st.code(", ".join(expected_columns))

        except Exception as e:
            st.error(f"⚠️ Error reading uploaded file: {e}")

    # === Restore from Backup ===
    st.sidebar.header("🧯 Restore Backup")
    backup_files = glob.glob(CSV_FILE.replace(".csv", "") + "_backup_*.csv")

    if backup_files:
        backup_files.sort(reverse=True)
        selected_backup = st.sidebar.selectbox("Choose a backup file to restore", backup_files)

        if st.sidebar.button("♻️ Restore Selected Backup"):
            try:
                shutil.copy(selected_backup, CSV_FILE)
            except PermissionError:
                st.error("❌ Cannot restore — please close the CSV file if it's open in Excel.")
            st.sidebar.success(f"✅ Restored data from: {os.path.basename(selected_backup)}")
            st.cache_data.clear()
            st.rerun()
    else:
        st.sidebar.info("No backup files found.")

    # === Add New Member ===
    st.sidebar.header("➕ Add New Member")
    with st.sidebar.form("add_form"):
        name = st.text_input("Name")
        phone = st.text_input("Phone")
        disability = st.text_input("Disability Type")
        age = st.text_input("Age")
        device = st.text_input("Assistive Device")
        subcounty = st.text_input("Sub-County")
        ward = st.text_input("Ward")
        submitted = st.form_submit_button("Add Member")

        if submitted:
            if name and disability and device and subcounty:
                new_row = pd.DataFrame([[name, phone, disability, age, device, subcounty, ward]],
                                       columns=["Name", "Phone", "Disability Type","Age", "Assistive Device", "Sub-County", "Ward"])
                df = pd.concat([df, new_row], ignore_index=True)
                df.to_csv(CSV_FILE, index=False)
                st.success(f"{name} has been added successfully.")
                st.cache_data.clear()
                st.rerun()
            else:
                st.warning("Please fill in at least Name, Disability, Device and Sub-County.")


# === Admin Review of Submitted Requests ===

    st.subheader("📝 Pending Member Requests")

    PENDING_FILE = "pending_requests.csv"

    if os.path.exists(PENDING_FILE):
        pending_df = pd.read_csv(PENDING_FILE)

        if not pending_df.empty:
            for i, row in pending_df.iterrows():
                with st.expander(f"{row['Name']} ({row['Phone']})"):
                    st.write(f"**Age:** {row['Age']}")
                    st.write(f"**Disability Type:** {row['Disability Type']}")
                    st.write(f"**Assistive Device:** {row['Assistive Device']}")
                    st.write(f"**Sub-County:** {row['Sub-County']}")
                    st.write(f"**Ward:** {row['Ward']}")

                col1, col2 = st.columns(2)
                if col1.button("✅ Approve", key=f"approve_{i}"):
                    # Append to main data
                    new_entry = pd.DataFrame([row])
                    df = pd.concat([df, new_entry], ignore_index=True)
                    df.to_csv(CSV_FILE, index=False)

                    # Remove from pending
                    pending_df = pending_df.drop(index=i).reset_index(drop=True)
                    pending_df.to_csv(PENDING_FILE, index=False)

                    st.success(f"Approved and added {row['Name']} to the main list.")
                    st.cache_data.clear()
                    st.rerun()

                if col2.button("❌ Reject", key=f"reject_{i}"):
                    # Remove from pending
                    pending_df = pending_df.drop(index=i).reset_index(drop=True)
                    pending_df.to_csv(PENDING_FILE, index=False)
                    st.warning(f"Rejected and removed {row['Name']} from the list.")
                    st.cache_data.clear()
                    st.rerun()
        else:
            st.info("✅ No pending requests at the moment.")
    else:
        st.info("No submissions have been made yet.")


# === Non-admin view ===
else:
    st.sidebar.warning("Admin login required to view or edit data.")




# === Sidebar: Filter Section ===
st.sidebar.header("🔎 Filter Data")

subcounty = st.sidebar.multiselect("Select Sub-County", df["Sub-County"].dropna().unique())

# 2. Dynamically filter ward options based on selected sub-county
if subcounty:
    filtered_wards = df[df["Sub-County"].isin(subcounty)]["Ward"].dropna().unique()
else:
    filtered_wards = df["Ward"].dropna().unique()

ward = st.sidebar.multiselect("Select Ward", filtered_wards)

# 3. Select Disability and Device as before
disability = st.sidebar.multiselect("Select Disability Type", df["Disability Type"].dropna().unique())
device = st.sidebar.multiselect("Select Assistive Device", df["Assistive Device"].dropna().unique())

# 4. Apply filters
filtered_df = df.copy()

if subcounty:
    filtered_df = filtered_df[filtered_df["Sub-County"].isin(subcounty)]

if ward:
    filtered_df = filtered_df[filtered_df["Ward"].isin(ward)]

if disability:
    filtered_df = filtered_df[filtered_df["Disability Type"].isin(disability)]

if device:
    filtered_df = filtered_df[filtered_df["Assistive Device"].isin(device)]


# === Main Title ===
st.image("C:/Users/IZOOH/Desktop/PWD/kitui_logo.jpg", width=150)
st.title("Kitui County PWD Assistive Device Needs Dashboard")

# === Filtered Table ===
st.subheader("📋 Filtered Data")
st.dataframe(filtered_df)

# === Summary ===
st.subheader("📊 Summary Stats")
st.write("Total entries:", len(filtered_df))
st.write("Unique Sub-Counties:", filtered_df["Sub-County"].nunique())
if not filtered_df.empty and not filtered_df['Assistive Device'].mode().empty:
    st.write("Most requested device:", filtered_df["Assistive Device"].mode()[0])
else:
    st.write("Most requested device: No data available.")

# === Chart ===
st.subheader("📊 Assistive Device Requests by Sub-County")
if not filtered_df.empty:
    chart_data = filtered_df["Sub-County"].value_counts()
    fig, ax = plt.subplots()
    chart_data.plot(kind="bar", ax=ax, color="orangered")
    ax.set_ylabel("Requests")
    ax.set_xlabel("Sub-County")
    ax.set_title("Device Requests by Sub-County")
    st.pyplot(fig)
else:
    st.info("No data to show in the chart.")

# === Name Search ===
st.sidebar.header("🔍 Search by Name")
name_query = st.sidebar.text_input("Enter full or partial name")

if name_query:
    name_filtered = df[df["Name"].str.contains(name_query, case=False, na=False)]
    st.subheader("👤 Person Lookup Result")
    if not name_filtered.empty:
        for index, row in name_filtered.iterrows():
            st.markdown(f"""
            **Name**: {row['Name']}  
            **Phone**: {row['Phone']}  
            **Disability Type**: {row['Disability Type']}  
            **Age**: {row['Age']}  
            **Assistive Device**: {row['Assistive Device']}  
            **Sub-County**: {row['Sub-County']}  
            **Ward**: {row['Ward']}  
            ---""")
    else:
        st.warning("No matching name found.")

# === Admin Login ===
st.subheader("🔐")

# Simple hardcoded password (can be moved to .env for better security)
password = st.text_input("Enter admin password", type="password", key="admindelete_password")
is_admin = password == "kitui123"  # 🔐 You can change this password


# === Delete Member (Searchable) ===
if is_admin:
    st.subheader("Delete a Member")

    delete_name = st.selectbox("Select a member to delete", df["Name"].unique(), key="delete_select")

    if delete_name:

     row_index = df[df["Name"] == delete_name].index[0]
     member = df.loc[row_index]

     with st.expander(f"Details of {delete_name}"):
        st.write(f"**Phone:** {member['Phone']}")
        st.write(f"**Disability Type:** {member['Disability Type']}")
        st.write(f"**Assistive Device:** {member['Assistive Device']}")
        st.write(f"**Sub-County:** {member['Sub-County']}")
        st.write(f"**Ward:** {member['Ward']}")

    if st.button(f"❌ Confirm Delete: {delete_name}", key="confirm_delete"):
        df = df.drop(index=row_index).reset_index(drop=True)
        df.to_csv(CSV_FILE, index=False)
        st.success(f"{delete_name} has been deleted.")
        st.cache_data.clear()
        st.rerun()
else:
  st.warning("Enter password to delete Members.")

# === Admin Login ===
st.subheader("🔐")

# Simple hardcoded password (can be moved to .env for better security)
password = st.text_input("Enter admin password", type="password", key="adminedit_password")
is_admin = password == "kitui123"  # 🔐 You can change this password

# === Edit Member Section ===
if is_admin:
 st.subheader("✏️ Edit Existing Member")

# Create a unique label per person using name + phone + location
 df["identifier"] = df["Name"] + " (" + df["Phone"] + " | " + df["Sub-County"] + " - " + df["Ward"] + ")"

# Dropdown showing each unique person
 selected_identifier = st.selectbox("Select a member to edit", df["identifier"])

# Find the selected row
 row_index = df[df["identifier"] == selected_identifier].index[0]
 member = df.loc[row_index]


# ✅ Save original phone before the form is filled
 original_phone = member["Phone"]

 with st.form("edit_form"):
    name = st.text_input("Name", value=member["Name"])
    phone = st.text_input("Phone", value=member["Phone"])
    disability = st.text_input("Disability Type", value=member["Disability Type"])
    age = st.text_input("Age", value=member.get("Age", ""))
    device = st.text_input("Assistive Device", value=member["Assistive Device"])
    subcounty = st.text_input("Sub-County", value=member["Sub-County"])
    ward = st.text_input("Ward", value=member["Ward"])
    submitted = st.form_submit_button("Update Member")

    if submitted:
        # ✅ Update ALL rows that match the original phone number
        matching_rows = df[df["Phone"] == original_phone].index

        for idx in matching_rows:
            df.at[idx, "Name"] = name
            df.at[idx, "Phone"] = phone
            df.at[idx, "Age"] = age
            df.at[idx, "Sub-County"] = subcounty
            df.at[idx, "Ward"] = ward
            # ✅ Keep their disability and device as-is

        # Save and cleanup
        df.drop(columns=["identifier"], inplace=True, errors="ignore")
        df.to_csv(CSV_FILE, index=False)
        st.success(f"✅ Updated all records for {name}.")
        st.cache_data.clear()
        st.rerun()

else:
  st.warning("Enter Password to Edit members.")
