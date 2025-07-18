
import streamlit as st
import os
from final_receipts_script import generate_receipt

st.set_page_config(page_title="Invoice Generator", layout="centered")

st.title("🧾 Invoice Generator - SMF&M")

with st.form("invoice_form"):
    st.subheader("Client & Invoice Details")

    invoice_number = st.text_input("Invoice Number", "INV0001")
    invoice_date = st.date_input("Invoice Date")
    client_name = st.text_input("Client Name")
    client_address = st.text_area("Client Address")
    client_gstin = st.text_input("Client GSTIN")
    client_phone = st.text_input("Client Mobile Number")
    city = st.text_input("City", "BENGALURU")
    transport = st.number_input("Transport Charge (₹)", min_value=0.0, step=100.0, format="%.2f")

    st.subheader("Item Entries (Add 1 by 1)")

    if "items" not in st.session_state:
        st.session_state.items = []

    desc = st.text_input("Description")
    qty = st.number_input("Quantity", min_value=0, step=1)
    rate = st.number_input("Rate", min_value=0.0, step=100.0, format="%.2f")

    if st.form_submit_button("➕ Add Item"):
        if desc and qty and rate:
            st.session_state.items.append({
                "description": desc,
                "quantity": qty,
                "rate": rate,
                "amount": qty * rate
            })
            st.experimental_rerun()

# Show item table
if st.session_state.get("items"):
    st.subheader("Current Items")
    st.table([
        {"Description": i["description"], "Qty": i["quantity"], "Rate": i["rate"], "Amount": i["amount"]}
        for i in st.session_state.items
    ])

# Final generate button
if st.session_state.get("items"):
    if st.button("✅ Generate Invoice"):
        meta = {
            "InvoiceNumber": invoice_number,
            "InvoiceDate": invoice_date.strftime("%b %d, %Y"),
            "ClientName": client_name,
            "ClientAddress": client_address,
            "ClientGST": client_gstin,
            "ClientPhone": client_phone,
            "City": city,
            "TransportAmount": str(transport)
        }

        filename = f"receipt_{invoice_number}.pdf"
        generate_receipt(meta, st.session_state.items, filename)

        with open(filename, "rb") as f:
            st.download_button("📥 Download Invoice", f, file_name=filename, mime="application/pdf")
