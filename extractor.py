"""extractor.py - pull fraud-relevant details out of pasted chat/receipt text.

Pure Python (re only). Built during Hacktoberfest '26 Hack Day.

extract_details(text) returns a dict:
    {
        "utr":    str | None,   # first 12-digit number that is not a +91 phone
        "upi_id": str | None,   # first name@handle (emails are skipped)
        "amount": str | None,   # first amount after Rs / Rs. / INR / rupee sign, commas removed
        "phones": list[str],    # unique 10-digit Indian mobiles, in order found
        "urls":   list[str],    # unique links, in order found
    }
Missing items give None (single values) or [] (lists). It never raises on empty input.
"""

import re

# Indian mobile: optional +91 / 91 prefix, then 10 digits starting 6-9 (a single space or hyphen
# is allowed after the first 5 digits, e.g. 98765 43210), not part of a longer number.
_PHONE_RE = re.compile(r"(?<!\d)(?:\+91[\s-]?|91[\s-]?)?([6-9]\d{4}[\s-]?\d{5})(?!\d)")
_UTR_RE = re.compile(r"(?<!\d)\d{12}(?!\d)")
# name@handle; the (?!\.[A-Za-z]) and \b stop emails like a@gmail.com from matching.
_UPI_RE = re.compile(r"[\w.\-]{2,}@[A-Za-z][A-Za-z0-9]{1,}\b(?!\.[A-Za-z])")
_AMOUNT_RE = re.compile(r"(?:₹|\bRs\.?|\bINR)\s*([\d,]*\d(?:\.\d{1,2})?)", re.IGNORECASE)
_URL_RE = re.compile(
    r"https?://[^\s<>\"']+|www\.[^\s<>\"']+|"
    r"\b(?:bit\.ly|tinyurl\.com|t\.me|wa\.me|rb\.gy|cutt\.ly)/[^\s<>\"']+",
    re.IGNORECASE,
)


def _unique(items):
    seen, out = set(), []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def extract_details(text):
    if not text or not isinstance(text, str):
        return {"utr": None, "upi_id": None, "amount": None, "phones": [], "urls": []}

    # Phones first, so a +91 98765 43210 style number is not mistaken for a UTR.
    phones, phone_spans = [], []
    for m in _PHONE_RE.finditer(text):
        phones.append(re.sub(r"\D", "", m.group(1)))
        phone_spans.append(m.span())

    utr = None
    for m in _UTR_RE.finditer(text):
        if any(s <= m.start() and m.end() <= e for s, e in phone_spans):
            continue
        utr = m.group(0)
        break

    upi_match = _UPI_RE.search(text)
    amount_match = _AMOUNT_RE.search(text)

    urls = [u.rstrip(".,;:!?)]}>'\"") for u in _URL_RE.findall(text)]

    return {
        "utr": utr,
        "upi_id": upi_match.group(0) if upi_match else None,
        "amount": amount_match.group(1).replace(",", "") if amount_match else None,
        "phones": _unique(phones),
        "urls": _unique(urls),
    }


if __name__ == "__main__":
    import json
    import sys

    print(json.dumps(extract_details(sys.stdin.read()), indent=2, ensure_ascii=False))
