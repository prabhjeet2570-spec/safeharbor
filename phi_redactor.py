"""
SafeHarbor — PHI detection and redaction.

Plain regex for now. It won't catch a name that doesn't follow "patient <Name>",
but it's enough to prove the pipeline works end to end before I reach for
anything heavier.

Usage:
    from phi_redactor import PHIRedactor

    redactor = PHIRedactor()
    result = redactor.analyze_and_redact("Patient John Doe, MRN 847291")
    print(result["redacted_text"])
"""

import re
import logging

logger = logging.getLogger("safeharbor.phi")


# ============================================================
# Patterns
# ============================================================

REGEX_PATTERNS = {
    "SSN": (r"\b\d{3}-\d{2}-\d{4}\b", "[REDACTED_SSN]"),
    "MRN": (r"\bMRN[\s:#]*\d{5,}\b", "MRN [REDACTED_MRN]"),
    "DOB": (
        r"\b(?:DOB|date\s*of\s*birth)[\s:]*\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
        "DOB [REDACTED_DOB]",
    ),
    "PHONE": (r"\b\d{3}[-.)]\s*\d{3}[-.)]\s*\d{4}\b", "[REDACTED_PHONE]"),
    "EMAIL": (
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "[REDACTED_EMAIL]",
    ),
    "PATIENT_NAME": (
        r"\b(?:patient|pt)[\s:]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b",
        "patient [REDACTED_NAME]",
    ),
    "ADDRESS": (
        r"\b\d{1,5}\s+[A-Z][a-z]+\s+(?:St|Ave|Blvd|Dr|Rd|Ln|Way|Court|Circle|Place)\b",
        "[REDACTED_ADDRESS]",
    ),
}


def regex_redact(text: str) -> dict:
    """Scan text for PHI patterns and replace every match."""
    redacted = text
    findings = []

    for entity_type, (pattern, replacement) in REGEX_PATTERNS.items():
        matches = list(re.finditer(pattern, redacted, re.IGNORECASE))
        if matches:
            for m in matches:
                findings.append(
                    {
                        "entity_type": entity_type,
                        "text": m.group(),
                        "start": m.start(),
                        "end": m.end(),
                        "score": 0.85,
                    }
                )
            redacted = re.sub(pattern, replacement, redacted, flags=re.IGNORECASE)

    return {
        "redacted_text": redacted,
        "findings": findings,
        "phi_detected": len(findings) > 0,
        "phi_count": len(findings),
        "entity_types_found": list(set(f["entity_type"] for f in findings)),
        "engine": "regex",
    }


# ============================================================
# Redactor
# ============================================================


class PHIRedactor:
    """Detect and redact PHI in a block of text."""

    def __init__(self):
        logger.info("Using regex-based PHI detection")

    def analyze_and_redact(self, text: str) -> dict:
        """
        Returns:
            {
                "redacted_text": "patient [REDACTED_NAME], MRN [REDACTED_MRN]...",
                "findings": [{"entity_type": "SSN", "text": "...", ...}, ...],
                "phi_detected": True,
                "phi_count": 3,
                "entity_types_found": ["SSN", "MRN"],
                "engine": "regex",
            }
        """
        if not text or not text.strip():
            return {
                "redacted_text": text,
                "findings": [],
                "phi_detected": False,
                "phi_count": 0,
                "entity_types_found": [],
                "engine": "none",
            }

        return regex_redact(text)

    def analyze_only(self, text: str) -> dict:
        """Detect PHI without redacting — used for risk scoring."""
        if not text or not text.strip():
            return {"findings": [], "phi_detected": False, "phi_count": 0}

        result = regex_redact(text)
        return {
            "findings": result["findings"],
            "phi_detected": result["phi_detected"],
            "phi_count": result["phi_count"],
        }


# ============================================================
# Quick self-test
# ============================================================

if __name__ == "__main__":
    redactor = PHIRedactor()

    test_cases = [
        "How do I implement quicksort in Python?",
        (
            "Summarize discharge notes: Patient John Michael Doe, "
            "MRN: 847291034, DOB: 03/15/1958, SSN: 423-91-8847, "
            "Phone: 555-867-5309, Email: johndoe@email.com"
        ),
    ]

    for i, text in enumerate(test_cases):
        result = redactor.analyze_and_redact(text)
        print(f"Test {i + 1}: PHI={result['phi_detected']} count={result['phi_count']}")
        print(f"  {result['redacted_text']}")
        print()
