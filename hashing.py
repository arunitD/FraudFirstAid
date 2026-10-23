"""
hashing.py - Cryptographic evidence hashing and timestamping for FraudFirstAid.
Computes standard SHA-256 digests on uploaded screenshots and generates ISO timestamps.
Hashes provide cryptographic proof that files have not been modified or tampered with.
"""

import hashlib
from datetime import datetime
from typing import Dict, Any


def calculate_sha256(file_bytes: bytes) -> str:
    """
    Computes hex SHA-256 digest of arbitrary file bytes using standard hashlib.
    """
    hasher = hashlib.sha256()
    hasher.update(file_bytes)
    return hasher.hexdigest()


def get_current_timestamp_iso() -> str:
    """
    Returns the current local date & time in ISO 8601 format with timezone indication.
    """
    return datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")


def process_evidence_file(file_name: str, file_bytes: bytes) -> Dict[str, Any]:
    """
    Takes an uploaded file's name and byte stream, calculates its SHA-256 digest,
    records the processing timestamp, and formats file size.

    Returns:
        Dictionary with filename, sha256, timestamp, and size_kb.
    """
    sha256_hash = calculate_sha256(file_bytes)
    timestamp = get_current_timestamp_iso()
    size_kb = round(len(file_bytes) / 1024, 2)

    return {
        "filename": file_name,
        "sha256": sha256_hash,
        "timestamp": timestamp,
        "size_kb": size_kb,
        "byte_count": len(file_bytes),
    }


def verify_file_integrity(file_bytes: bytes, recorded_hash: str) -> bool:
    """
    Verifies if file bytes match the recorded SHA-256 hash.
    Used for tamper verification.
    """
    calculated = calculate_sha256(file_bytes)
    return calculated.lower() == recorded_hash.strip().lower()
