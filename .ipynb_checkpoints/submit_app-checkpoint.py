import streamlit as st
import pandas as pd
import os

CSV_FILE = "pending_requests.csv"

# Step 1: Show sub-county selection outside the form
st.title("📥 Submit Your Assistive Device Request")

# Define subcounty-ward map (place this at the top)
subcounty_ward_map = {
    "Kitui Central": ["Township", "Kyangwithya West", "Miambani", "Nzambani"],
    "Kitui East": ["Nzambani", "Voo/Kyamatu", "Mtito/Kaliku", "Zombe/Mwitika", "Chuluni"],
    "Kitui South": ["Ikanga/Kyatune", "Mutomo", "Athi", "Kanziko","Ikutha/Kasaala" ],
    "Kitui West": ["Kauwi", "Matinyani", "Kwa Mutonga/Kithumula","Mutonguni"],
    "Kitui Rural": ["Kisasi", "Mbitini", "Kwa Vonza/Wote", "Kanyangi"],
    "Mwingi North": ["Tseikuru","Kyuso","Mumoni","Tharaka","Ngomeni","Katse"],
    "Mwingi Central": ["Central","Kivou","Nguni","Nuu","Mui","Waita"],
    "Mwing West": ["Migwani", "Nguutani", "Kyome/Thaana", "Kiomo/Kyethani"],
}

# Select sub-county FIRST (outside the form)
subcounty = st.selectbox("Sub-County", list(subcounty_ward_map.keys()))

# Get wards dynamically for the selected subcounty
ward_options = subcounty_ward_map.get(subcounty, [])

# Step 2: Form starts here
with st.form("public_form"):
    name = st.text_input("Full Name")
    phone = st.text_input("Phone")
    age = st.text_input("Age")
    disability = st.text_input("Disability Type")
    device = st.text_input("Assistive Device")

    # Ward select is now dynamically linked
    ward = st.selectbox("Ward", ward_options)

    submitted = st.form_submit_button("Submit Request")




import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email_notification(name, phone, age, disability, device, subcounty, ward):
    sender = "mukungiisaac86@gmail.com"
    receiver = "mukungiisaac86@gmail.com"
    password = "xksw xqln yorp fvvh"  # Use app password from Google

    subject = "🔔 New Assistive Device Request Submitted"

    body = f"""
    A new request has been submitted:

    Name: {name}
    Phone: {phone}
    Age: {age}
    Disability Type: {disability}
    Assistive Device: {device}
    Sub-County: {subcounty}
    Ward: {ward}
    """

    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = receiver
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, receiver, msg.as_string())
    except Exception as e:
        st.error(f"❌ Failed to send email notification: {e}")



if submitted:
    if not all([name.strip(), phone.strip(), age.strip(), disability.strip(), device.strip(), subcounty.strip(), ward.strip()]):
        st.warning("⚠️ Please fill in all required fields.")
    else:
        new_row = pd.DataFrame([[name, phone, age, disability, device, subcounty, ward]],
            columns=["Name", "Phone", "Age", "Disability Type", "Assistive Device", "Sub-County", "Ward"])

        csv_file = "pending_requests.csv"

        if os.path.exists(csv_file):
            existing = pd.read_csv(csv_file)
            new_row = pd.concat([existing, new_row], ignore_index=True)

        new_row.to_csv(csv_file, index=False)

        # ✅ Now it's safe to send email/whatsapp notification
        # send_email_notification(...)
        # send_whatsapp_notification(...)
        send_email_notification(name, phone, age, disability, device, subcounty, ward)

        st.success("✅ Your request has been submitted for review.")







