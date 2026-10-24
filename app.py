"""
FraudFirstAid - Emergency First-Aid Kit for Victims of Online Financial Fraud in India
Runs locally with no API keys, using only streamlit, hashlib, and reportlab.
"""

import streamlit as st
from datetime import datetime
from extractor import extract_details

# Local helper modules
from validators import validate_utr, validate_upi_id, validate_phone, validate_amount
from hashing import process_evidence_file
from generators import (
    generate_1930_script,
    generate_bank_dispute_letter,
    generate_cybercrime_portal_text,
    amount_in_inr_format,
)
from pdf_pack import generate_pdf_pack


# ---------------------------------------------------------
# Page Configuration & Clean Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="FraudFirstAid India - Cyber Financial Fraud Kit",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom styling for high readability and emergency response ergonomics
st.markdown(
    """
    <style>
    .main-title {
        color: #b91c1c;
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        color: #4b5563;
        font-size: 1.05rem;
        margin-bottom: 1.2rem;
    }
    .urgent-banner {
        background-color: #fee2e2;
        border-left: 6px solid #dc2626;
        padding: 14px 18px;
        border-radius: 6px;
        color: #991b1b;
        margin-bottom: 20px;
        font-weight: 500;
    }
    .stDownloadButton button {
        background-color: #b91c1c !important;
        color: white !important;
        font-weight: 600 !important;
        border-radius: 6px !important;
    }
    .stDownloadButton button:hover {
        background-color: #991b1b !important;
    }
    .footer-disclaimer {
        margin-top: 40px;
        padding: 16px;
        border-top: 1px solid #e5e7eb;
        background-color: #f9fafb;
        border-radius: 8px;
        font-size: 0.85rem;
        color: #6b7280;
        text-align: center;
        line-height: 1.5;
    }
    .hash-badge {
        font-family: monospace;
        background-color: #f1f5f9;
        padding: 2px 6px;
        border-radius: 4px;
        color: #1e3a8a;
        font-size: 0.8rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# Session State Initialization & Demo Data
# ---------------------------------------------------------
DEMO_DATA = {
    "scam_type": "Fake job offer",
    "name": "Aarav Sharma",
    "phone": "9876543210",
    "datetime": datetime.now(),
    "amount": 47500.0,
    "utr": "428719043215",
    "upi_id": "express.tasks99@ybl",
    "bank_name": "State Bank of India (SBI)",
    "branch": "Raj Nagar Extension, Ghaziabad",
    "email": "aarav.sharma@example.com",
    "description": (
        "Received a message on WhatsApp promising ₹3,500/day for writing reviews on Google Maps. "
        "Was then directed to a Telegram group 'Global Merchant Rating Task Force'. "
        "Completed 3 initial trial tasks and received ₹250 payout. "
        "Next, was instructed to deposit ₹47,500 to unlock 'VIP Task 4' with a promised return of ₹68,000. "
        "Once payment was sent via UPI to express.tasks99@ybl, the admins deleted the chat and blocked my number."
    ),
    "specifics": {
        "job_platform": "Telegram (@ReviewGlobalAdmin) & WhatsApp",
        "task_description": "Rating hotels and restaurants on Google Maps for commission",
        "fake_portal_url": "https://fast-tasks-ratings-vip.cc",
        "promised_vs_deposited": "Promised ₹68,000 return for depositing ₹47,500",
    },
}

if "form_loaded" not in st.session_state:
    st.session_state["name"] = ""
    st.session_state["phone"] = ""
    st.session_state["datetime"] = datetime.now()
    st.session_state["amount"] = 0.0
    st.session_state["utr"] = ""
    st.session_state["upi_id"] = ""
    st.session_state["bank_name"] = "State Bank of India (SBI)"
    st.session_state["description"] = ""
    st.session_state["scam_type"] = "Fake job offer"
    st.session_state["specifics"] = {}
    st.session_state["form_loaded"] = True


def load_demo():
    """Fills session state with a realistic fictional fraud case."""
    st.session_state["name"] = DEMO_DATA["name"]
    st.session_state["phone"] = DEMO_DATA["phone"]
    st.session_state["datetime"] = DEMO_DATA["datetime"]
    st.session_state["amount"] = DEMO_DATA["amount"]
    st.session_state["utr"] = DEMO_DATA["utr"]
    st.session_state["upi_id"] = DEMO_DATA["upi_id"]
    st.session_state["bank_name"] = DEMO_DATA["bank_name"]
    st.session_state["description"] = DEMO_DATA["description"]
    st.session_state["scam_type"] = DEMO_DATA["scam_type"]
    st.session_state["branch"] = DEMO_DATA["branch"]
    st.session_state["email"] = DEMO_DATA["email"]
    st.session_state["specifics"] = DEMO_DATA["specifics"].copy()


# ---------------------------------------------------------
# Sidebar - Emergency Information & Demo Button
# ---------------------------------------------------------
with st.sidebar:
    st.image(
        "https://raw.githubusercontent.com/lucide-icons/lucide/main/icons/shield-alert.svg",
        width=50,
    )
    st.title("FraudFirstAid")
    st.caption("Immediate Documentation Kit for Cyber Crime Victims in India")

    st.markdown("---")
    st.markdown("### ⚡ Quick Demo")
    st.caption("Click below to populate a full realistic case and test the generators:")
    if st.button("📂 Load Demo Data", use_container_width=True, type="secondary"):
        load_demo()
        st.success("Fictional case loaded! Check fields below.")

    st.markdown("---")
    st.markdown("### 🚨 Emergency Contacts (India)")
    st.markdown(
        """
        - **1930** — National Cyber Crime Helpline (24x7)
        - **cybercrime.gov.in** — National Reporting Portal
        - **14448** — RBI Financial Grievance Helpline
        - **112** — National Emergency Police Helpline
        """
    )

    st.markdown("---")
    st.markdown("### ⏳ Golden Hour Rule")
    st.info(
        "Report within the **first 2-3 hours** of the fraudulent debit. "
        "The 1930 system can immediately freeze the stolen amount at the recipient's bank "
        "before it is siphoned or withdrawn from ATMs."
    )


# ---------------------------------------------------------
# Main Page Header
# ---------------------------------------------------------
st.markdown('<div class="main-title">🛡️ FraudFirstAid</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">Rapid documentation, tamper-evident evidence hashing, and official filings for victims of Indian financial cyber fraud. Runs 100% locally with zero external API keys.</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="urgent-banner">
        ⚠️ <b>Act Fast:</b> If your fraud occurred within the last 2 hours, immediately dial <b>1930</b>. 
        Use the read-aloud script generated below to give the operator the exact 12-digit UTR, UPI ID, and amounts needed to freeze the thief's account.
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# STEP 1: Scam Type & Dynamic Specific Questions
# ---------------------------------------------------------
st.subheader("Step 1: Select Scam Type")

scam_options = ["Fake job offer", "KYC fraud", "Investment scam", "Other"]
default_scam_index = scam_options.index(st.session_state.get("scam_type", "Fake job offer"))

selected_scam = st.selectbox(
    "What kind of cyber fraud occurred?",
    options=scam_options,
    index=default_scam_index,
    help="Selecting a category reveals specific targeted questions needed by cybercrime police.",
)
st.session_state["scam_type"] = selected_scam

# Dynamic Questions per Scam Type
st.markdown("##### 🔍 Scam-Specific Questions:")
scam_specifics = {}

if selected_scam == "Fake job offer":
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        scam_specifics["job_platform"] = st.text_input(
            "Platform where contacted (e.g., Telegram handle, WhatsApp number):",
            value=st.session_state.get("specifics", {}).get("job_platform", ""),
            placeholder="e.g. Telegram @JobOffersGlobal or +91 9123456789",
        )
        scam_specifics["task_description"] = st.text_input(
            "Type of task promised (e.g., Google Maps review, YouTube like, Telegram task):",
            value=st.session_state.get("specifics", {}).get("task_description", ""),
            placeholder="e.g. Rating hotels on Google Maps / watching YouTube videos",
        )
    with col_s2:
        scam_specifics["fake_portal_url"] = st.text_input(
            "Fake website / task portal URL:",
            value=st.session_state.get("specifics", {}).get("fake_portal_url", ""),
            placeholder="e.g. https://vip-review-task.cc",
        )
        scam_specifics["promised_vs_deposited"] = st.text_input(
            "Promised payout vs deposited amount:",
            value=st.session_state.get("specifics", {}).get("promised_vs_deposited", ""),
            placeholder="e.g. Deposited ₹47,500 for promised return of ₹68,000",
        )

elif selected_scam == "KYC fraud":
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        scam_specifics["impersonated_entity"] = st.text_input(
            "Entity impersonated (e.g., SBI, HDFC, Electricity Board, Jio/Airtel KYC):",
            value=st.session_state.get("specifics", {}).get("impersonated_entity", "State Bank of India (SBI) KYC Cell"),
            placeholder="e.g. SBI YONO / Electricity Bill Dept",
        )
        scam_specifics["malicious_app_name"] = st.text_input(
            "Malicious APK name or Screen-sharing app downloaded (if any):",
            value=st.session_state.get("specifics", {}).get("malicious_app_name", ""),
            placeholder="e.g. AnyDesk, TeamViewer QuickSupport, sbi_update.apk",
        )
    with col_s2:
        scam_specifics["sms_sender_id"] = st.text_input(
            "SMS Sender Header / Call Number:",
            value=st.session_state.get("specifics", {}).get("sms_sender_id", ""),
            placeholder="e.g. VM-SBIBNK, DZ-ELECT, or mobile number",
        )
        scam_specifics["threat_used"] = st.text_input(
            "Threat/Pretext used:",
            value=st.session_state.get("specifics", {}).get("threat_used", ""),
            placeholder="e.g. Account will be deactivated in 24 hours / Power will be cut tonight",
        )

elif selected_scam == "Investment scam":
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        scam_specifics["trading_platform_name"] = st.text_input(
            "Name of fraudulent trading/crypto platform or website:",
            value=st.session_state.get("specifics", {}).get("trading_platform_name", ""),
            placeholder="e.g. ProTrade-Max, BinanceVIP-India.vip, QuantGlobal",
        )
        scam_specifics["referral_or_mentor"] = st.text_input(
            "Referral agent, mentor, or WhatsApp group name:",
            value=st.session_state.get("specifics", {}).get("referral_or_mentor", ""),
            placeholder="e.g. 'Prof. Sharma Institutional Stock Tips #4'",
        )
    with col_s2:
        scam_specifics["scheme_type"] = st.text_input(
            "Scheme type (e.g., Institutional IPO allotment, Forex, Crypto mining):",
            value=st.session_state.get("specifics", {}).get("scheme_type", ""),
            placeholder="e.g. Guaranteed 30% weekly return on Institutional IPO shares",
        )
        scam_specifics["withdrawal_excuse"] = st.text_input(
            "Excuse given when you tried to withdraw money:",
            value=st.session_state.get("specifics", {}).get("withdrawal_excuse", ""),
            placeholder="e.g. Demanded 20% 'tax deposit' or account frozen by SEBI",
        )

else:  # Other
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        scam_specifics["modus_operandi"] = st.text_input(
            "Primary method used (e.g., OLX QR code, courier customs fee, lottery):",
            value=st.session_state.get("specifics", {}).get("modus_operandi", ""),
            placeholder="e.g. Buyer sent fake QR code saying 'scan to receive money'",
        )
    with col_s2:
        scam_specifics["perpetrator_handles"] = st.text_input(
            "Known fraudster numbers, email addresses, or handles:",
            value=st.session_state.get("specifics", {}).get("perpetrator_handles", ""),
            placeholder="e.g. +91 9811223344, support@customsclearance.in",
        )

st.session_state["specifics"] = scam_specifics
st.markdown("---")


# ---------------------------------------------------------
# STEP 2: Incident & Transaction Fields with Real-time Validation
# ---------------------------------------------------------
st.subheader("Step 2: Incident & Transaction Details")
with st.expander("⚡ Auto-fill from a pasted chat or SMS (optional)"):
    pasted_text = st.text_area(
        "Paste the scam chat, bank SMS or payment message here:",
        height=140,
        key="paste_box",
    )
    if st.button("🔎 Extract details", key="extract_btn"):
        found = extract_details(pasted_text or "")
        filled = []
        if found.get("utr"):
            st.session_state["utr"] = found["utr"]
            filled.append("UTR")
        if found.get("upi_id"):
            st.session_state["upi_id"] = found["upi_id"]
            filled.append("UPI ID")
        if found.get("amount"):
            st.session_state["amount"] = float(found["amount"])
            filled.append("Amount")
        if filled:
            st.success("Filled in: " + ", ".join(filled))
        else:
            st.warning("No UTR, UPI ID or amount found in that text.")
        if found.get("phones"):
            st.info("Phone numbers found (possible fraudster numbers): " + ", ".join(found["phones"]))
        if found.get("urls"):
            st.info("Links found: " + ", ".join(found["urls"]))

col1, col2 = st.columns(2)

with col1:
    name_input = st.text_input(
        "Victim Full Name (as per Bank Account) *",
        value=st.session_state.get("name", ""),
        placeholder="e.g. Aarav Sharma",
    )
    st.session_state["name"] = name_input

    phone_input = st.text_input(
        "Registered Mobile Number *",
        value=st.session_state.get("phone", ""),
        placeholder="10-digit Indian Mobile Number (e.g. 9876543210)",
        max_chars=14,
    )
    st.session_state["phone"] = phone_input
    is_phone_valid, phone_err = validate_phone(phone_input) if phone_input else (False, "")
    if phone_input and not is_phone_valid:
        st.caption(f":red[⚠️ {phone_err}]")

    dt_input = st.date_input(
        "Date of Fraudulent Transaction *",
        value=st.session_state.get("datetime", datetime.now()),
    )
    if "txn_time" not in st.session_state:
        st.session_state["txn_time"] = datetime.now().time().replace(second=0, microsecond=0)
    time_input = st.time_input("Time of Transaction *", value=st.session_state["txn_time"])
    st.session_state["txn_time"] = time_input
    combined_dt = f"{dt_input} {time_input.strftime('%H:%M:%S')}"
    st.session_state["datetime"] = combined_dt

    amount_input = st.number_input(
        "Fraud Amount in ₹ (INR) *",
        min_value=0.0,
        max_value=100000000.0,
        value=float(st.session_state.get("amount", 0.0)),
        step=500.0,
        format="%.2f",
    )
    st.session_state["amount"] = amount_input
    is_amount_valid, amount_err = validate_amount(amount_input)
    if amount_input > 0:
        st.caption(f":green[Amount Formatted: **{amount_in_inr_format(amount_input)}**]")
    elif amount_input == 0:
        st.caption(":red[⚠️ Please specify an amount greater than ₹0]")

with col2:
    bank_list = [
        "State Bank of India (SBI)",
        "HDFC Bank",
        "ICICI Bank",
        "Punjab National Bank (PNB)",
        "Bank of Baroda",
        "Axis Bank",
        "Kotak Mahindra Bank",
        "Canara Bank",
        "Union Bank of India",
        "IndusInd Bank",
        "Other Bank / Payment Bank",
    ]
    cur_bank = st.session_state.get("bank_name", "State Bank of India (SBI)")
    bank_idx = bank_list.index(cur_bank) if cur_bank in bank_list else len(bank_list) - 1
    selected_bank = st.selectbox("Your Debited Bank Name *", options=bank_list, index=bank_idx)

    if selected_bank == "Other Bank / Payment Bank":
        custom_bank = st.text_input("Specify Bank / Wallet / Payment Bank Name:", value="")
        st.session_state["bank_name"] = custom_bank if custom_bank else "Other Bank"
    else:
        st.session_state["bank_name"] = selected_bank

    # UTR Validation: Exactly 12 digits, show error as the user types
    utr_input = st.text_input(
        "12-Digit UTR / RRN (Transaction Reference) *",
        value=st.session_state.get("utr", ""),
        placeholder="Enter exactly 12 numeric digits (e.g. 428719043215)",
        max_chars=16,
        help="Unique Transaction Reference found in your bank SMS, UPI app receipt, or statement.",
    )
    st.session_state["utr"] = utr_input
    is_utr_valid, utr_err = validate_utr(utr_input) if utr_input else (False, "UTR is required (exactly 12 digits).")
    if utr_input:
        if not is_utr_valid:
            st.error(f"❌ UTR Error: {utr_err}")
        else:
            st.success("✅ Valid 12-digit UTR confirmed.")

    # UPI ID Validation: user@bank format
    upi_input = st.text_input(
        "Fraudster / Beneficiary UPI ID (VPA) *",
        value=st.session_state.get("upi_id", ""),
        placeholder="e.g. scammer99@ybl, refund.desk@okhdfcbank",
        help="The UPI handle where money was transferred.",
    )
    st.session_state["upi_id"] = upi_input
    is_upi_valid, upi_err = validate_upi_id(upi_input) if upi_input else (False, "UPI ID is required.")
    if upi_input:
        if not is_upi_valid:
            st.error(f"❌ UPI ID Error: {upi_err}")
        else:
            st.success(f"✅ Valid UPI ID format ({upi_input})")
    branch_input = st.text_input(
        "Bank Branch Name / City (optional)",
        value=st.session_state.get("branch", ""),
        placeholder="e.g. Raj Nagar Extension, Ghaziabad",
    )
    st.session_state["branch"] = branch_input

    email_input = st.text_input(
        "Your Email (optional)",
        value=st.session_state.get("email", ""),
        placeholder="e.g. aarav.sharma@example.com",
    )
    st.session_state["email"] = email_input

desc_input = st.text_area(
    "Short Incident Description / Sequence of Events *",
    value=st.session_state.get("description", ""),
    placeholder="Describe step-by-step how you were approached, what you were told, and how the transfer occurred.",
    height=110,
)
st.session_state["description"] = desc_input
st.markdown("---")


# ---------------------------------------------------------
# STEP 3: Multi-Screenshot Upload & SHA-256 Hashing
# ---------------------------------------------------------
st.subheader("Step 3: Screenshot Evidence & Cryptographic Hashing")
st.caption(
    "Upload screenshots of WhatsApp/Telegram chats, payment receipts, SMS alerts, or fake websites. "
    "Every file is cryptographically hashed with **SHA-256** and stamped with intake time to preserve digital integrity."
)

uploaded_files = st.file_uploader(
    "Choose screenshot files (PNG, JPG, JPEG, WEBP, PDF)",
    type=["png", "jpg", "jpeg", "webp", "pdf"],
    accept_multiple_files=True,
    help="Select multiple files showing the conversation, payment confirmation, and fraudster profiles.",
)

processed_evidence = []
if uploaded_files:
    for f in uploaded_files:
        file_bytes = f.read()
        ev_record = process_evidence_file(f.name, file_bytes)
        processed_evidence.append(ev_record)

    st.markdown(f"**Recorded {len(processed_evidence)} Evidence File(s):**")
    
    # Render table of files, SHA-256 hashes, timestamps
    cols_header = st.columns([3, 2, 2, 5])
    cols_header[0].markdown("**File Name**")
    cols_header[1].markdown("**Size**")
    cols_header[2].markdown("**Intake Timestamp**")
    cols_header[3].markdown("**SHA-256 Checksum**")

    for ev in processed_evidence:
        c1, c2, c3, c4 = st.columns([3, 2, 2, 5])
        c1.markdown(f"📄 `{ev['filename']}`")
        c2.markdown(f"{ev['size_kb']} KB")
        c3.markdown(f"{ev['timestamp']}")
        c4.markdown(f'<span class="hash-badge">{ev["sha256"]}</span>', unsafe_allow_html=True)

    st.success("🔒 SHA-256 tamper-evident integrity seals computed successfully.")
else:
    st.info("ℹ️ No screenshots uploaded yet. You can upload screenshots now or test using the pre-loaded fields.")

st.markdown("---")


# ---------------------------------------------------------
# STEP 4: Generated Emergency Outputs
# ---------------------------------------------------------
st.subheader("Step 4: Emergency First-Aid Outputs")
st.caption("All documents are generated instantly from your inputs. Review on screen and download immediately.")

# Pack form data
case_data = {
    "name": st.session_state["name"],
    "phone": st.session_state["phone"],
    "datetime": st.session_state["datetime"],
    "amount": st.session_state["amount"],
    "utr": st.session_state["utr"],
    "upi_id": st.session_state["upi_id"],
    "bank_name": st.session_state["bank_name"],
    "description": st.session_state["description"],
    "scam_type": st.session_state["scam_type"],
    "scam_specifics": st.session_state.get("specifics", {}),
    "branch": st.session_state.get("branch", ""),
    "email": st.session_state.get("email", ""),
}

# Validation summary check
form_ready = (
    bool(case_data["name"])
    and is_utr_valid
    and is_upi_valid
    and (case_data["amount"] > 0)
)

if not form_ready:
    st.warning("⚠️ Please provide at least a Name, valid 12-digit UTR, valid UPI ID, and Amount to generate full official outputs.")

# Generate output strings
script_1930 = generate_1930_script(case_data, processed_evidence)
bank_letter = generate_bank_dispute_letter(case_data, processed_evidence)
cybercrime_text = generate_cybercrime_portal_text(case_data, processed_evidence)

# Generate PDF pack bytes
try:
    pdf_bytes = generate_pdf_pack(case_data, processed_evidence)
except Exception as e:
    pdf_bytes = b""
    st.error(f"Error compiling PDF: {e}")

tab1, tab2, tab3, tab4 = st.tabs([
    "📞 1930 Helpline Read-Aloud Script",
    "🏦 Bank Dispute / Chargeback Letter",
    "💻 cybercrime.gov.in Complaint Text",
    "📑 PDF Evidence Pack (Dossier)",
])

with tab1:
    st.markdown("#### Read-Aloud Script for Calling 1930 Helpline")
    st.caption("Keep this open on your screen when you dial 1930. Read it sentence-by-sentence to the police operator.")
    st.text_area("1930 Script Content", value=script_1930, height=340, key=f"txt_1930_{abs(hash(script_1930))}")
    
    col_d1, _ = st.columns([2, 5])
    with col_d1:
        st.download_button(
            label="📥 Download 1930 Script (.txt)",
            data=script_1930,
            file_name=f"1930_Helpline_Script_UTR_{case_data['utr'] or 'pending'}.txt",
            mime="text/plain",
            use_container_width=True,
        )

with tab2:
    st.markdown("#### Bank Dispute & Chargeback Letter")
    st.caption("Submit via email to your bank's Nodal Officer and print a physical copy for your home branch.")
    st.text_area("Bank Letter Content", value=bank_letter, height=340, key=f"txt_bank_{abs(hash(bank_letter))}")
    
    col_d2, _ = st.columns([2, 5])
    with col_d2:
        st.download_button(
            label="📥 Download Bank Dispute Letter (.txt)",
            data=bank_letter,
            file_name=f"Bank_Dispute_Letter_{case_data['bank_name'][:10].replace(' ', '_')}_{case_data['utr'] or 'pending'}.txt",
            mime="text/plain",
            use_container_width=True,
        )

with tab3:
    st.markdown("#### Structured Text for cybercrime.gov.in Portal")
    st.caption("Copy and paste each section directly into the National Cyber Crime Reporting Portal complaint form.")
    st.text_area("Portal Complaint Content", value=cybercrime_text, height=340, key=f"txt_cyber_{abs(hash(cybercrime_text))}")
    
    col_d3, _ = st.columns([2, 5])
    with col_d3:
        st.download_button(
            label="📥 Download Cybercrime Portal Draft (.txt)",
            data=cybercrime_text,
            file_name=f"Cybercrime_Portal_Draft_{case_data['utr'] or 'pending'}.txt",
            mime="text/plain",
            use_container_width=True,
        )

with tab4:
    st.markdown("#### Multi-Page PDF Evidence Pack")
    st.caption(
        "Official compilation including Incident Summary, Fraud Specifics, Chronological Timeline, "
        "and SHA-256 Cryptographic Evidence Integrity Table with victim declaration."
    )
    if pdf_bytes:
        st.success(f"✅ PDF Evidence Dossier ready ({len(pdf_bytes):,} bytes).")
        col_d4, _ = st.columns([2, 5])
        with col_d4:
            st.download_button(
                label="📥 Download PDF Evidence Pack (.pdf)",
                data=pdf_bytes,
                file_name=f"FraudFirstAid_Evidence_Dossier_UTR_{case_data['utr'] or 'draft'}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
    else:
        st.warning("PDF could not be compiled. Please ensure reportlab is installed.")


# ---------------------------------------------------------
# Footer Disclaimer (Mandatory Requirement)
# ---------------------------------------------------------
st.markdown(
    """
    <div class="footer-disclaimer">
        ⚖️ <b>DISCLAIMER:</b> FraudFirstAid is a documentation aid only and does not constitute legal advice. 
        It does not replace calling the 1930 cyber helpline, notifying your bank's fraud desk, or lodging an official FIR with the police. 
        Cryptographic SHA-256 hashes demonstrate that digital evidence files have not been modified or tampered with since creation; 
        they do not verify or attest to the substantive authenticity of the underlying claims.
    </div>
    """,
    unsafe_allow_html=True,
)
