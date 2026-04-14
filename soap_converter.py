#Code Obtained from claude.ai with the prompt: "Can you help me write a python function that takes a string version of a SOAP note and converts it to json? There's a risk there might be special characters I need to strip, namely asterisks."

import re

def soap_note_to_json(soap_text: str, strip_chars: str = "*") -> dict:
    """
    Convert a SOAP note string to a structured JSON-compatible dict.

    Args:
        soap_text:    The raw SOAP note as a string.
        strip_chars:  Characters to strip from values (default: asterisks).

    Returns:
        A dict with keys: subjective, objective, assessment, plan.
        Any section not found will have a value of None.
    """
    # Strip specified special characters from the entire text first
    clean_text = soap_text
    for ch in strip_chars:
        clean_text = clean_text.replace(ch, "")

    # Regex: match each SOAP section header and capture everything until the next header or end
    pattern = re.compile(
        r"(?i)\b(subjective|objective|assessment|plan)\b[:\-]?\s*(.*?)(?=\b(?:subjective|objective|assessment|plan)\b[:\-]?|$)",
        re.DOTALL
    )

    result = {
        "subjective": None,
        "objective": None,
        "assessment": None,
        "plan": None,
    }

    for match in pattern.finditer(clean_text):
        section = match.group(1).lower()
        content = match.group(2).strip()
        if section in result:
            result[section] = content if content else None

    return result