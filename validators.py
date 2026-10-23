"""
validators.py - Input validation functions for FraudFirstAid India.
Validates Indian financial transaction details, UTR, UPI ID, phone, and amounts.
"""

import re
from typing import Tuple

# Regex pattern for 12-digit Indian Bank UTR (Unique Transaction Reference) / RRN
# UTRs for IMPS, NEFT, RTGS, and UPI in India are standard 12-digit numeric codes.
UTR_PATTERN = re.compile(r"^\d{12}$")

# Regex pattern for Indian UPI Virtual Payment Address (VPA)
# Typically username@psp (e.g. rahul@oksbi, fraudster.store@ybl, merchant@icici)
UPI_PATTERN = re.compile(r"^[a-zA-Z0-9.\-_]{2,64}@[a-zA-Z0-9.\-_]{2,32}$")

# Regex for standard 10-digit Indian Mobile Numbers starting with 6, 7, 8, or 9
PHONE_PATTERN = re.compile(r"^[6-9]\d{9}$")


def validate_utr(utr: str) -> Tuple[bool, str]:
    """
    Validates that a UTR (Unique Transaction Reference) is exactly 12 numeric digits.

    Returns:
        (is_valid, error_message): Tuple containing validation boolean and feedback.
    """
    cleaned = utr.strip()
    if not cleaned:
        return False, "UTR is required. Must be exactly 12 digits."
    
    if not cleaned.isdigit():
        return False, f"UTR must contain digits only (found non-numeric characters)."
    
    length = len(cleaned)
    if length < 12:
        return False, f"UTR too short ({length}/12 digits entered). Exactly 12 digits required."
    elif length > 12:
        return False, f"UTR too long ({length}/12 digits entered). Exactly 12 digits required."
    
    return True, ""


def validate_upi_id(upi_id: str) -> Tuple[bool, str]:
    """
    Validates Indian UPI ID (VPA) format like 'handle@bank'.

    Returns:
        (is_valid, error_message): Tuple containing validation boolean and feedback.
    """
    cleaned = upi_id.strip()
    if not cleaned:
        return False, "UPI ID is required (e.g., receiver@okhdfcbank)."
    
    if "@" not in cleaned:
        return False, "UPI ID must contain '@' separating the identifier and bank handle."
    
    parts = cleaned.split("@")
    if len(parts) != 2:
        return False, "UPI ID cannot contain multiple '@' symbols."
    
    user_part, handle_part = parts[0], parts[1]
    if len(user_part) < 2:
        return False, "Identifier before '@' is too short."
    if len(handle_part) < 2:
        return False, "Bank/PSP handle after '@' is too short (e.g., @paytm, @okhdfcbank)."

    if not UPI_PATTERN.match(cleaned):
        return False, "Invalid UPI ID format. Allowed characters: letters, numbers, dot, hyphen, underscore."
    
    return True, ""


def validate_phone(phone: str) -> Tuple[bool, str]:
    """
    Validates 10-digit Indian mobile number.
    """
    cleaned = re.sub(r"[\s\-\+]", "", phone.strip())
    if cleaned.startswith("91") and len(cleaned) == 12:
        cleaned = cleaned[2:]
    elif cleaned.startswith("0") and len(cleaned) == 11:
        cleaned = cleaned[1:]

    if not cleaned:
        return False, "Phone number is required."
    if not cleaned.isdigit():
        return False, "Phone number must contain digits only."
    if len(cleaned) != 10:
        return False, f"Phone number must be 10 digits (got {len(cleaned)} digits)."
    if not PHONE_PATTERN.match(cleaned):
        return False, "Indian mobile numbers must start with 6, 7, 8, or 9."

    return True, ""


def validate_amount(amount_val) -> Tuple[bool, str]:
    """
    Validates that the fraud loss amount is a positive number.
    """
    try:
        val = float(amount_val)
        if val <= 0:
            return False, "Amount must be greater than ₹0."
        if val > 100000000:
            return False, "Amount exceeds ₹10 Crore limit."
        return True, ""
    except (ValueError, TypeError):
        return False, "Please enter a valid numeric amount in ₹."
