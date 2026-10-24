from extractor import extract_details


def test_fake_job_chat():
    text = (
        "Hi, selected for data entry job! Pay Rs. 1,500 registration to rahul.hr99@okaxis. "
        "Call +91 98765 43210. Apply: https://jobs-hiring-now.xyz/apply."
    )
    r = extract_details(text)
    assert r["upi_id"] == "rahul.hr99@okaxis"
    assert r["amount"] == "1500"
    assert r["phones"] == ["9876543210"]
    assert r["urls"] == ["https://jobs-hiring-now.xyz/apply"]
    assert r["utr"] is None


def test_receipt():
    text = "Payment successful. ₹25,000.50 paid to 9123456780@ybl. UTR: 407812345678. Ref 12/10/2026"
    r = extract_details(text)
    assert r["utr"] == "407812345678"
    assert r["amount"] == "25000.50"
    assert r["upi_id"] == "9123456780@ybl"


def test_kyc_scam_with_prefixed_phone_not_utr():
    text = "Your SBI KYC expires today. Call 919876543210 or visit bit.ly/sbi-kyc-update now. INR 10,000 blocked."
    r = extract_details(text)
    assert r["utr"] is None  # 12 digits but it is a 91 + mobile number
    assert r["phones"] == ["9876543210"]
    assert r["urls"] == ["bit.ly/sbi-kyc-update"]
    assert r["amount"] == "10000"


def test_email_is_not_upi():
    r = extract_details("Mail me at scammer@gmail.com for the offer")
    assert r["upi_id"] is None


def test_empty_and_none():
    empty = {"utr": None, "upi_id": None, "amount": None, "phones": [], "urls": []}
    assert extract_details("") == empty
    assert extract_details(None) == empty
    assert extract_details("nothing useful here") == empty


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
