import re
import json

def extract_fields(text: str) -> dict:
    fields = {}

    # Look for dollar amounts like $1,250.00 or $500
    amount_matches = re.findall(r"\$\s?[\d,]+\.?\d*", text)
    if amount_matches:
        fields["amounts_found"] = amount_matches

    # Look for dates like 03/15/2026, 3-15-2026, or March 15 2026
    date_matches = re.findall(
        r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b",
        text,
    )
    if date_matches:
        fields["dates_found"] = date_matches

    return fields

def fields_to_json(fields: dict) -> str:
    return json.dumps(fields)