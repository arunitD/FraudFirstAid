"""
generators.py - Document and script generator for FraudFirstAid India.
Generates:
  1. 1930 Helpline Read-Aloud Script (CFCFRMS / Citizen Financial Cyber Fraud Reporting)
  2. Formal Bank Dispute & Chargeback Letter (compliant with RBI circulars)
  3. Structured Cybercrime.gov.in Complaint Text

All three generators take lang="en" (default) or lang="hi".
UTR numbers, UPI IDs, amounts and user-entered text are never translated.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional

RECENT_HOURS = 3  # incidents newer than this get the urgent wording


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _norm_lang(lang: Optional[str]) -> str:
    return "hi" if str(lang or "en").strip().lower().startswith("hi") else "en"


def _get(data: Dict[str, Any], key: str, fallback: str) -> str:
    """data.get(key) but also falls back when the value is None / empty / spaces."""
    value = data.get(key)
    if value is None or str(value).strip() == "":
        return fallback
    return str(value).strip()


def hours_since_incident(dt_value: Any) -> Optional[float]:
    """
    Hours between the incident and now, or None if the time can't be read
    (or only a date without a time was given).
    """
    if dt_value is None:
        return None

    dt = None
    if isinstance(dt_value, datetime):
        dt = dt_value
    else:
        s = str(dt_value).strip()
        if len(s) <= 10:  # date only, no time -> can't judge hours
            return None
        try:
            dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        except ValueError:
            for fmt in (
                "%d/%m/%Y %H:%M",
                "%d-%m-%Y %H:%M",
                "%Y-%m-%d %H:%M",
                "%d %b %Y %H:%M",
                "%d/%m/%Y %I:%M %p",
                "%d-%m-%Y %I:%M %p",
            ):
                try:
                    dt = datetime.strptime(s, fmt)
                    break
                except ValueError:
                    continue
    if dt is None:
        return None

    now = datetime.now(dt.tzinfo) if dt.tzinfo is not None else datetime.now()
    hours = (now - dt).total_seconds() / 3600
    if hours < -1:  # time in the future -> unreliable
        return None
    return max(hours, 0.0)


def is_recent(data: Dict[str, Any]) -> bool:
    h = hours_since_incident(data.get("datetime"))
    return h is not None and h < RECENT_HOURS


def format_utr_spaced(utr: str) -> str:
    """Formats 12-digit UTR with spaces for effortless read-aloud: '1 2 3 4  5 6 7 8  9 0 1 2'"""
    cleaned = utr.strip()
    if len(cleaned) == 12:
        return f"{cleaned[0:4]} {cleaned[4:8]} {cleaned[8:12]} (Spoken digit-by-digit: {' '.join(list(cleaned))})"
    return cleaned


def format_utr_spaced_hi(utr: str) -> str:
    cleaned = utr.strip()
    if len(cleaned) == 12:
        return f"{cleaned[0:4]} {cleaned[4:8]} {cleaned[8:12]} (एक-एक अंक करके बोलें: {' '.join(list(cleaned))})"
    return cleaned


def amount_in_inr_format(amount: float) -> str:
    """Formats number in Indian Rupees format, e.g., ₹1,25,000.00"""
    try:
        val = float(amount)
        s = f"{val:,.2f}"
        return f"₹{s}"
    except Exception:
        return f"₹{amount}"


def _letter_date(data: Dict[str, Any], placeholder: str) -> str:
    raw = data.get("datetime")
    if raw is None or str(raw).strip() == "":
        return placeholder
    s = str(raw)
    return s.split("T")[0] if "T" in s else s


# ---------------------------------------------------------------------------
# 1. 1930 helpline script
# ---------------------------------------------------------------------------

def generate_1930_script(data: Dict[str, Any], evidence_list: List[Dict[str, Any]], lang: str = "en") -> str:
    """
    Generates a clear read-aloud script for the victim when calling
    National Cyber Crime Reporting Helpline 1930.
    Urgent wording is used only if the incident is under ~3 hours old.
    """
    lang = _norm_lang(lang)
    recent = is_recent(data)
    when = _get(data, "datetime", "N/A")

    amount_str = amount_in_inr_format(data.get("amount", 0))
    scam_type = data.get("scam_type", "Financial Cyber Fraud")
    scam_specifics = data.get("scam_specifics", {}) or {}

    specifics_text = ""
    for k, v in scam_specifics.items():
        if v:
            clean_k = k.replace("_", " ").title()
            specifics_text += f"   • {clean_k}: {v}\n"

    n_ev = len(evidence_list) if evidence_list else 0

    if lang == "hi":
        utr_spaced = format_utr_spaced_hi(str(data.get("utr", "")))
        evidence_summary = (
            f"{n_ev} स्क्रीनशॉट SHA-256 हैश के साथ सुरक्षित किए गए हैं" if n_ev
            else "फ़ोन में स्क्रीनशॉट सुरक्षित हैं"
        )
        if recent:
            opening = (
                "नमस्ते, मैं एक ऑनलाइन वित्तीय साइबर धोखाधड़ी की शिकायत दर्ज कराने के लिए कॉल कर रहा/रही हूँ। "
                "यह घटना कुछ ही घंटे पहले की है। मेरे बैंक खाते से धोखाधड़ी वाला लेनदेन हुआ है। "
                "चूँकि अभी शुरुआती घंटे (गोल्डन आवर) चल रहे हैं, कृपया प्राप्तकर्ता खाते को जल्द से जल्द फ्रीज़ करवाएँ।"
            )
            closing_req = (
                f"अधिकारी महोदय, कृपया UTR {data.get('utr', '')} CFCFRMS पोर्टल के ज़रिए प्राप्तकर्ता बैंक और UPI स्विच को भेजें "
                "और संदिग्ध खाते पर जल्द से जल्द LIEN / FREEZE लगवाएँ, ताकि पैसा आगे न जाए।"
            )
        else:
            opening = (
                f"नमस्ते, मैं एक ऑनलाइन वित्तीय साइबर धोखाधड़ी की शिकायत दर्ज कराने के लिए कॉल कर रहा/रही हूँ। "
                f"यह घटना {when if when != 'N/A' else 'नीचे बताई गई तारीख'} को हुई थी। मेरे बैंक खाते से धोखाधड़ी वाला लेनदेन हुआ है "
                "और पैसा मेरे खाते से जा चुका है। कृपया प्राप्तकर्ता खाते को फ्लैग करवाएँ और उसमें जो भी रकम बची हो उस पर होल्ड या फ्रीज़ लगवाएँ।"
            )
            closing_req = (
                f"अधिकारी महोदय, कृपया UTR {data.get('utr', '')} CFCFRMS पोर्टल के ज़रिए प्राप्तकर्ता बैंक और UPI स्विच को भेजें, "
                "संदिग्ध खाते को जाँच के लिए फ्लैग करें और उसमें बची हुई रकम पर LIEN / FREEZE लगवाएँ।"
            )

        script = f"""================================================================================
🚨 1930 राष्ट्रीय साइबर हेल्पलाइन - पढ़कर बोलने की स्क्रिप्ट
नागरिक वित्तीय साइबर धोखाधड़ी रिपोर्टिंग एवं प्रबंधन प्रणाली (CFCFRMS)
================================================================================
कॉल करने से पहले:
- अपना आधार / पैन कार्ड और बैंक खाता नंबर पास रखें।
- शांत और साफ़ आवाज़ में बोलें। साफ़ कहें कि प्राप्तकर्ता खाते को फ्लैग / फ्रीज़ किया जाए।
- फ़ोन रखने से पहले अधिकारी से अपना 14 अंकों का शिकायत पावती नंबर (ACKNOWLEDGEMENT NUMBER) ज़रूर माँगें।
================================================================================

[ऑपरेटर: "राष्ट्रीय साइबर हेल्पलाइन 1930, मैं आपकी क्या मदद कर सकता/सकती हूँ?"]

आप यह पढ़कर बोलें:

"{opening}

मेरी घटना का विवरण इस प्रकार है:
1. मेरा पूरा नाम: {data.get('name', 'N/A')}
2. मेरा पंजीकृत मोबाइल नंबर: {data.get('phone', 'N/A')}
3. जिस बैंक से पैसा कटा उसका नाम: {data.get('bank_name', 'N/A')}
4. घटना की तारीख और समय: {when}
5. कुल धोखाधड़ी की रकम: {amount_str}

लेनदेन की पहचान (अंतर-बैंक फ्रीज़ के लिए ज़रूरी):
6. 12 अंकों का ट्रांज़ैक्शन UTR / RRN नंबर:
   --> {utr_spaced}

7. धोखेबाज़ की UPI ID / VPA:
   --> {data.get('upi_id', 'N/A')}

धोखाधड़ी का प्रकार:
8. श्रेणी: {scam_type}
{specifics_text}
घटना कैसे हुई, संक्षेप में:
"{data.get('description', 'धोखाधड़ी भरे संदेश / कॉल के ज़रिए अनधिकृत लेनदेन करवाया गया।')}"

सबूत की स्थिति:
मेरे पास {evidence_summary}, जिन्हें मैं cybercrime.gov.in पर अपलोड करूँगा/करूँगी।

अंतिम अनुरोध:
"{closing_req}
कृपया मुझे मेरी शिकायत का पावती नंबर दें।"
================================================================================
"""
        return script.strip()

    # ---- English ----
    utr_spaced = format_utr_spaced(str(data.get("utr", "")))
    evidence_summary = (
        f"{n_ev} screenshot(s) recorded with SHA-256 hashes" if n_ev
        else "screenshots captured on phone"
    )

    if recent:
        opening = (
            "Hello, I am calling to report a financial cyber fraud that happened a short while ago, within the last few hours. "
            "A fraudulent transaction was made from my bank account. "
            "Since these are the first few hours (the Golden Hour), I request that the beneficiary account be frozen as quickly as possible."
        )
        closing_req = (
            f"Officer, please transmit the UTR {data.get('utr', '')} through the CFCFRMS portal to the beneficiary bank and UPI switch "
            "and mark a LIEN / FREEZE on the suspect account as early as possible, before the funds move further."
        )
    else:
        opening = (
            "Hello, I am calling to report a financial cyber fraud that took place on "
            f"{when if when != 'N/A' else 'the date given below'}. "
            "A fraudulent transaction was made from my bank account and the money has already left my account. "
            "I request that the beneficiary account be flagged and that a hold or freeze be placed on any funds that remain in it."
        )
        closing_req = (
            f"Officer, please transmit the UTR {data.get('utr', '')} through the CFCFRMS portal to the beneficiary bank and UPI switch, "
            "flag the suspect account for investigation, and request a LIEN / FREEZE on any funds that remain in it."
        )

    script = f"""================================================================================
🚨 1930 NATIONAL CYBER HELPLINE - READ-ALOUD SCRIPT
Citizen Financial Cyber Fraud Reporting & Management System (CFCFRMS)
================================================================================
TIPS BEFORE YOU DIAL:
- Keep your Aadhaar / PAN card and bank account number handy.
- Speak calmly and clearly. Clearly ask for the beneficiary account to be flagged / frozen.
- Ask the agent for your 14-digit ACKNOWLEDGEMENT NUMBER before hanging up.
================================================================================

[OPERATOR ANSWERS: "National Cyber Helpline 1930, how can I help you?"]

YOU READ ALOUD:

"{opening}

Here are my primary incident details:
1. MY FULL NAME: {data.get('name', 'N/A')}
2. MY REGISTERED MOBILE NUMBER: {data.get('phone', 'N/A')}
3. MY DEBITED BANK NAME: {data.get('bank_name', 'N/A')}
4. FRAUD INCIDENT DATE & TIME: {when}
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
I have {evidence_summary}, ready to upload to cybercrime.gov.in.

CLOSING REQUEST:
"{closing_req}
Please give me my complaint acknowledgement number."
================================================================================
"""
    return script.strip()


# ---------------------------------------------------------------------------
# 2. Bank dispute letter
# ---------------------------------------------------------------------------

def generate_bank_dispute_letter(data: Dict[str, Any], evidence_list: List[Dict[str, Any]], lang: str = "en") -> str:
    """
    Generates a formal bank dispute and chargeback notice citing RBI guidelines
    on customer liability in unauthorized electronic banking transactions.
    Uses data["branch"] and data["email"] when present, else the old placeholders.
    """
    lang = _norm_lang(lang)
    amount_str = amount_in_inr_format(data.get("amount", 0))

    if lang == "hi":
        branch = _get(data, "branch", "[अपनी स्थानीय शाखा का नाम / शहर लिखें]")
        email = _get(data, "email", "[आपका पंजीकृत ईमेल]")
        letter_date = _letter_date(data, "[तारीख]")

        evidence_rows = ""
        if evidence_list:
            for idx, ev in enumerate(evidence_list, 1):
                evidence_rows += (
                    f"   संलग्नक {idx}: {ev.get('filename')} "
                    f"(SHA-256: {str(ev.get('sha256', ''))[:16]}... | समय: {ev.get('timestamp')})\n"
                )
        else:
            evidence_rows = "   संलग्नक: लेनदेन विवरण और भुगतान के स्क्रीनशॉट की प्रतियाँ संलग्न हैं।\n"

        letter = f"""सेवा में,
शाखा प्रबंधक / नोडल साइबर शिकायत अधिकारी,
{data.get('bank_name', '[बैंक का नाम]')},
शाखा: {branch}

दिनांक: {letter_date}

विषय: अनधिकृत धोखाधड़ी वाले लेनदेन के लिए तत्काल विवाद सूचना तथा रिवर्सल / LIEN मार्किंग का अनुरोध
संदर्भ: UTR / RRN नं. {data.get('utr', '[12 अंकों का UTR]')} | रकम: {amount_str}

आदरणीय महोदय / महोदया,

मैं आपके बैंक में अपने खाते से हुए एक अनधिकृत / धोखाधड़ी वाले इलेक्ट्रॉनिक वित्तीय लेनदेन की औपचारिक शिकायत तुरंत दर्ज कराना चाहता/चाहती हूँ।

I. खाताधारक का विवरण:
• खाताधारक का नाम: {data.get('name', '[आपका नाम]')}
• पंजीकृत मोबाइल नंबर: {data.get('phone', '[आपका मोबाइल नंबर]')}
• बैंक का नाम: {data.get('bank_name', '[बैंक का नाम]')}

II. विवादित लेनदेन का विवरण:
• लेनदेन की तारीख और समय: {data.get('datetime', '[तारीख और समय]')}
• विवादित रकम: {amount_str}
• यूनिक ट्रांज़ैक्शन रेफ़रेंस (UTR / RRN): {data.get('utr', '[UTR नंबर]')}
• धोखेबाज़ की UPI ID / खाता: {data.get('upi_id', '[प्राप्तकर्ता UPI]')}
• घटना का प्रकार: {data.get('scam_type', 'साइबर वित्तीय धोखाधड़ी')}

III. धोखाधड़ी का सारांश:
{data.get('description', 'यह लेनदेन धोखे से, बिना मेरी वास्तविक सहमति के करवाया गया।')}

IV. नियामक संदर्भ एवं तत्काल अपेक्षित कार्रवाई:
1. भारतीय रिज़र्व बैंक (RBI) के परिपत्र RBI/2017-18/15 (DBR.No.Leg.BC.78/09.07.005/2017-18) "ग्राहक संरक्षण – अनधिकृत इलेक्ट्रॉनिक बैंकिंग लेनदेन में ग्राहकों की देयता सीमित करना" के अनुसार, मैं आपके बैंक को शून्य / सीमित देयता की सूचना अवधि के भीतर तुरंत सूचित कर रहा/रही हूँ।
2. UPI के लिए NPCI की विवाद प्रबंधन प्रणाली (DMS) के दिशानिर्देशों के तहत, मेरा अनुरोध है कि आप प्राप्तकर्ता के पेमेंट सर्विस प्रोवाइडर (PSP) और गंतव्य बैंक के पास चार्जबैक / फ्रॉड रिकॉल अनुरोध तुरंत दर्ज करें।
3. कृपया NPCI के साइबर फ्रॉड डेस्क और राज्य पुलिस के साइबर सेल के साथ समन्वय करें, ताकि गंतव्य बैंक उस धोखाधड़ी वाले खाते पर तुरंत LIEN / DEBIT FREEZE लगाए जिसमें UTR {data.get('utr', '')} से संबंधित रकम जमा हुई है।
4. मैंने इस मामले की सूचना राष्ट्रीय साइबर अपराध हेल्पलाइन 1930 / cybercrime.gov.in पर भी दे दी है।

V. संलग्न सबूत:
{evidence_rows}
मेरा अनुरोध है कि आप इस शिकायत के लिए औपचारिक विवाद पावती संदर्भ संख्या जारी करें और RBI के निर्देशों के अनुसार अस्थायी क्रेडिट / रिवर्सल उपलब्ध कराएँ।

भवदीय,

{data.get('name', '[हस्ताक्षर / नाम]')}
संपर्क: {data.get('phone', '[फ़ोन नंबर]')}
ईमेल: {email}
"""
        return letter.strip()

    # ---- English ----
    branch = _get(data, "branch", "[Insert Your Local Branch Name / City]")
    email = _get(data, "email", "[Your Registered Email]")
    letter_date = _letter_date(data, "[Date and Time]")

    evidence_rows = ""
    if evidence_list:
        for idx, ev in enumerate(evidence_list, 1):
            evidence_rows += (
                f"   Annexure {idx}: {ev.get('filename')} "
                f"(SHA-256: {str(ev.get('sha256', ''))[:16]}... | Timestamp: {ev.get('timestamp')})\n"
            )
    else:
        evidence_rows = "   Annexures: Transaction statement and payment screenshot copies attached.\n"

    letter = f"""To,
The Branch Manager / Nodal Cyber Grievance Officer,
{data.get('bank_name', '[Bank Name]')},
Branch: {branch}

Date: {letter_date}

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
Email: {email}
"""
    return letter.strip()


# ---------------------------------------------------------------------------
# 3. cybercrime.gov.in portal text
# ---------------------------------------------------------------------------

def generate_cybercrime_portal_text(data: Dict[str, Any], evidence_list: List[Dict[str, Any]], lang: str = "en") -> str:
    """
    Generates structured plain text formatted specifically for copy-paste into
    the fields of https://cybercrime.gov.in (National Cyber Crime Reporting Portal).
    """
    lang = _norm_lang(lang)
    amount_str = str(data.get("amount", 0))
    scam_specifics = data.get("scam_specifics", {}) or {}

    if lang == "hi":
        scam_type = data.get("scam_type", "वित्तीय धोखाधड़ी")
        portal_text = f"""=== CYBERCRIME.GOV.IN पोर्टल शिकायत का मसौदा ===
(नीचे के हिस्सों को https://cybercrime.gov.in के नागरिक रिपोर्टिंग फ़ॉर्म में कॉपी-पेस्ट करें)

[भाग 1: घटना की श्रेणी]
शिकायत की श्रेणी: वित्तीय धोखाधड़ी / साइबर बैंकिंग धोखाधड़ी
उप-श्रेणी: {scam_type}

[भाग 2: लेनदेन का विवरण]
बैंक का नाम: {data.get('bank_name', '')}
लेनदेन की तारीख और समय: {data.get('datetime', '')}
कटी हुई रकम (₹): {amount_str}
12 अंकों का UTR / RRN / रेफ़रेंस नंबर: {data.get('utr', '')}
संदिग्ध / प्राप्तकर्ता की UPI ID: {data.get('upi_id', '')}

[भाग 3: संदिग्ध से जुड़ी विशेष जानकारी]
"""
        for k, v in scam_specifics.items():
            if v:
                clean_k = k.replace("_", " ").title()
                portal_text += f"{clean_k}: {v}\n"

        portal_text += f"""
[भाग 4: घटना का पूरा विवरण (नैरेटिव बॉक्स में पेस्ट करें)]
{data.get('datetime', 'बताई गई तारीख')} को मेरे बैंक खाते ({data.get('bank_name', 'बैंक')}) से ₹{amount_str} की रकम धोखाधड़ी से, मेरी अनुमति के बिना निकाल ली गई।

यह घटना {scam_type} की श्रेणी में आती है।
घटना का क्रम:
{data.get('description', '')}

इस लेनदेन का यूनिक ट्रांज़ैक्शन रेफ़रेंस (UTR) {data.get('utr', '')} है और रकम संदिग्ध UPI ID {data.get('upi_id', '')} में जमा हुई है।
मैंने 1930 हेल्पलाइन और अपनी बैंक शाखा से संपर्क करके प्राप्तकर्ता खाते को फ्रीज़ करने का अनुरोध किया है।

[भाग 5: हैश किए गए सबूत की फ़ाइलें (संलग्न फ़ाइलों की सूची)]
"""
        if evidence_list:
            for idx, ev in enumerate(evidence_list, 1):
                portal_text += f"{idx}. फ़ाइल: {ev.get('filename')} | SHA-256: {ev.get('sha256')} | अपलोड समय: {ev.get('timestamp')}\n"
        else:
            portal_text += "UPI डेबिट सूचना, चैट हिस्ट्री और प्राप्तकर्ता भुगतान पेज के स्क्रीनशॉट संलग्न हैं।\n"

        portal_text += """
[अनुरोध / माँगी गई राहत]
मेरा अनुरोध है कि साइबर क्राइम जाँच प्रकोष्ठ UTR और UPI ID से जुड़े प्राप्तकर्ता बैंक खाते का पता लगाए, निकाली गई रकम ज़ब्त करे, धोखेबाज़ के संचार हैंडल / SIM कार्ड ब्लॉक करे, और सूचना प्रौद्योगिकी अधिनियम 2000 तथा भारतीय न्याय संहिता (BNS) के तहत आवश्यक कानूनी कार्रवाई शुरू करे।
"""
        return portal_text.strip()

    # ---- English ----
    scam_type = data.get("scam_type", "Financial Fraud")

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