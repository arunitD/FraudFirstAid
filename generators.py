"""
generators.py - Document and script generator for FraudFirstAid India.
Generates:
  1. 1930 Helpline Read-Aloud Script (CFCFRMS / Citizen Financial Cyber Fraud Reporting)
  2. Formal Bank Dispute & Chargeback Letter (compliant with RBI circulars)
  3. Structured Cybercrime.gov.in Complaint Text
"""

from typing import Dict, Any, List


def format_utr_spaced(utr: str) -> str:
    """Formats 12-digit UTR with spaces for effortless read-aloud: '1 2 3 4  5 6 7 8  9 0 1 2'"""
    cleaned = utr.strip()
    if len(cleaned) == 12:
        return f"{cleaned[0:4]} {cleaned[4:8]} {cleaned[8:12]} (Spoken digit-by-digit: {' '.join(list(cleaned))})"
    return cleaned


def amount_in_inr_format(amount: float) -> str:
    """Formats number in Indian Rupees format, e.g., ₹1,25,000.00"""
    try:
        val = float(amount)
        s = f"{val:,.2f}"
        return f"₹{s}"
    except Exception:
        return f"₹{amount}"


def generate_1930_script(data: Dict[str, Any], evidence_list: List[Dict[str, Any]]) -> str:
    """
    Generates an urgent, clear read-aloud script for the victim when calling
    National Cyber Crime Reporting Helpline 1930.
    """
    utr_spaced = format_utr_spaced(str(data.get("utr", "")))
    amount_str = amount_in_inr_format(data.get("amount", 0))

    scam_type = data.get("scam_type", "Financial Cyber Fraud")
    scam_specifics = data.get("scam_specifics", {})

    specifics_text = ""
    for k, v in scam_specifics.items():
        if v:
            clean_k = k.replace("_", " ").title()
            specifics_text += f"   • {clean_k}: {v}\n"

    evidence_summary = f"{len(evidence_list)} screenshot(s) recorded with SHA-256 hashes" if evidence_list else "Screenshots captured on phone"

    script = f"""================================================================================
🚨 1930 NATIONAL CYBER HELPLINE - READ-ALOUD SCRIPT
Citizen Financial Cyber Fraud Reporting & Management System (CFCFRMS)
================================================================================
TIPS BEFORE YOU DIAL:
- Keep your Aadhaar / PAN card and bank account number handy.
- Speak calmly and clearly. Emphasize "GOLDEN HOUR ACCOUNT FREEZE".
- Ask the agent for your 14-digit ACKNOWLEDGEMENT NUMBER before hanging up.
================================================================================

[OPERATOR ANSWERS: "National Cyber Helpline 1930, how can I help you?"]

YOU READ ALOUD:

"Hello, I am calling to report an ongoing financial cyber fraud under the Golden Hour protocol.
A fraudulent transaction was just made from my bank account, and I urgently need the beneficiary account frozen.

Here are my primary incident details:
1. MY FULL NAME: {data.get('name', 'N/A')}
2. MY REGISTERED MOBILE NUMBER: {data.get('phone', 'N/A')}
3. MY DEBITED BANK NAME: {data.get('bank_name', 'N/A')}
4. FRAUD INCIDENT DATE & TIME: {data.get('datetime', 'N/A')}
5. TOTAL FRAUDULENT AMOUNT: {amount_str}

TRANSACTION IDENTIFIERS (CRITICAL FOR INTER-BANK FREEZE):
6. 12-DIGIT TRANSACTION UTR / RRN NUMBER:
   --> {utr_spaced}

7. FRAUDSTER'S BENEFICIARY UPI ID / VPA:
   --> {data.get('upi_id', 'N/A')}

NATURE OF FRAUD:
8. SCAM CATEGORY: {scam_type}
{specifics_text}
BRIEF SUMMARY OF HOW IT HAPPENED:
"{data.get('description', 'Unauthorized transaction was induced through fraudulent communication.')}"

EVIDENCE STATUS:
I have already timestamped and hashed {evidence_summary} to upload to cybercrime.gov.in.

CLOSING REQUEST:
"Officer, please immediately transmit the UTR {data.get('utr', '')} through the CFCFRMS portal to the beneficiary bank and UPI switch to mark a LIEN / FREEZE on the suspect account before the money is siphoned out.
Please give me my complaint acknowledgement number."
================================================================================
"""
    return script.strip()


def generate_bank_dispute_letter(data: Dict[str, Any], evidence_list: List[Dict[str, Any]]) -> str:
    """
    Generates a formal bank dispute and chargeback notice citing RBI guidelines
    on customer liability in unauthorized electronic banking transactions.
    """
    amount_str = amount_in_inr_format(data.get("amount", 0))

    evidence_rows = ""
    if evidence_list:
        for idx, ev in enumerate(evidence_list, 1):
            evidence_rows += f"   Annexure {idx}: {ev.get('filename')} (SHA-256: {ev.get('sha256')[:16]}... | Timestamp: {ev.get('timestamp')})\n"
    else:
        evidence_rows = "   Annexures: Transaction statement and payment screenshot copies attached.\n"

    letter = f"""To,
The Branch Manager / Nodal Cyber Grievance Officer,
{data.get('bank_name', '[Bank Name]')},
Branch: [Insert Your Local Branch Name / City]

Date: {data.get('datetime', '[Date and Time]').split('T')[0] if 'T' in str(data.get('datetime', '')) else str(data.get('datetime', '[Date]'))}

SUBJECT: URGENT DISPUTE NOTICE & REQUEST FOR IMMEDIATE REVERSAL / LIEN MARKING FOR UNAUTHORIZED FRAUDULENT TRANSACTION
REF: UTR / RRN NO. {data.get('utr', '[12-Digit UTR]')} | AMOUNT: {amount_str}

Respected Sir / Madam,

I am writing this formal complaint to immediately report an unauthorized / fraudulent electronic financial transaction debited from my account held with your esteemed bank.

I. ACCOUNT & VICTIM DETAILS:
• Account Holder Name: {data.get('name', '[Your Name]')}
• Registered Mobile Number: {data.get('phone', '[Your Mobile Number]')}
• Bank Name: {data.get('bank_name', '[Bank Name]')}

II. DISPUTED TRANSACTION PARTICULARS:
• Transaction Date & Time: {data.get('datetime', '[Date & Time]')}
• Disputed Amount: {amount_str}
• Unique Transaction Reference (UTR / RRN): {data.get('utr', '[UTR Number]')}
• Fraudster Beneficiary UPI ID / Account: {data.get('upi_id', '[Beneficiary UPI]')}
• Incident Nature / Modus Operandi: {data.get('scam_type', 'Cyber Financial Fraud')}

III. SUMMARY OF FRAUD:
{data.get('description', 'The fraudulent transaction was executed without genuine authorization through fraudulent misrepresentation.')}

IV. REGULATORY REFERENCES & IMMEDIATE REMEDIES SOUGHT:
1. As per Reserve Bank of India (RBI) Circular RBI/2017-18/15 (DBR.No.Leg.BC.78/09.07.005/2017-18) on "Customer Protection – Limiting Liability of Customers in Unauthorised Electronic Banking Transactions", I am notifying your bank immediately within the zero/limited liability notification window.
2. Under NPCI Dispute Management System (DMS) guidelines for UPI, I request you to urgently raise a chargeback / fraud recall request with the beneficiary's Payment Service Provider (PSP) and destination bank.
3. Kindly coordinate with the cyber fraud desk at NPCI and state police cyber cell to instruct the destination bank to place an immediate LIEN / DEBIT FREEZE on the fraudulent account where funds associated with UTR {data.get('utr', '')} were credited.
4. I have also reported this matter to the National Cyber Crime Helpline 1930 / cybercrime.gov.in.

V. ATTACHED EVIDENCE:
{evidence_rows}
I request you to issue a formal dispute acknowledgment reference number for this complaint and provide a provisional credit / reversal as per RBI mandates.

Yours faithfully,

{data.get('name', '[Signature / Name]')}
Contact: {data.get('phone', '[Phone Number]')}
Email: [Your Registered Email]
"""
    return letter.strip()


def generate_cybercrime_portal_text(data: Dict[str, Any], evidence_list: List[Dict[str, Any]]) -> str:
    """
    Generates structured plain text formatted specifically for copy-paste into
    the fields of https://cybercrime.gov.in (National Cyber Crime Reporting Portal).
    """
    amount_str = str(data.get("amount", 0))
    scam_type = data.get("scam_type", "Financial Fraud")
    scam_specifics = data.get("scam_specifics", {})

    portal_text = f"""=== CYBERCRIME.GOV.IN PORTAL COMPLAINT DRAFT ===
(Copy-paste relevant sections into the Citizen Reporting form at https://cybercrime.gov.in)

[SECTION 1: INCIDENT CATEGORY]
Category of Complaint: Financial Fraud / Cyber Banking Fraud
Sub-Category: {scam_type}

[SECTION 2: TRANSACTION DETAILS]
Bank Name: {data.get('bank_name', '')}
Transaction Date & Time: {data.get('datetime', '')}
Amount Debited (₹): {amount_str}
12-Digit UTR / RRN / Reference No: {data.get('utr', '')}
Suspect / Beneficiary UPI ID: {data.get('upi_id', '')}

[SECTION 3: SUSPECT SPECIFIC PARTICULARS]
"""
    for k, v in scam_specifics.items():
        if v:
            clean_k = k.replace("_", " ").title()
            portal_text += f"{clean_k}: {v}\n"

    portal_text += f"""
[SECTION 4: COMPREHENSIVE INCIDENT DESCRIPTION (Paste into Narrative Box)]
On {data.get('datetime', 'the stated date')}, an unauthorized fraudulent transaction amounting to ₹{amount_str} was fraudulently debited from my bank account at {data.get('bank_name', 'bank')}. 

The incident occurred under the category of {scam_type}. 
Narrative of events:
{data.get('description', '')}

The transaction bears the Unique Transaction Reference (UTR) {data.get('utr', '')} credited to suspect UPI ID {data.get('upi_id', '')}. 
I have already contacted the 1930 helpline and my bank branch to request an immediate freeze of the beneficiary account.

[SECTION 5: EVIDENCE FILES HASHED (List of attached files)]
"""
    if evidence_list:
        for idx, ev in enumerate(evidence_list, 1):
            portal_text += f"{idx}. File: {ev.get('filename')} | SHA-256: {ev.get('sha256')} | Upload Timestamp: {ev.get('timestamp')}\n"
    else:
        portal_text += "Screenshots of UPI debit notification, chat history, and beneficiary payment page attached.\n"

    portal_text += """
[PRAYER / RELIEF SOUGHT]
I request the Cyber Crime Investigation Cell to trace the beneficiary bank account linked to UTR and UPI ID, seize the siphoned amount, block the fraudster's communication handles/SIM cards, and initiate necessary criminal proceedings under the Information Technology Act 2000 and the Bharatiya Nyaya Sanhita (BNS).
"""
    return portal_text.strip()
