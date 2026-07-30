"""Run the extraction and map the result into a procurement record.

Box AI returns ``vendor`` as a nested object and ``delivery_schedule`` as
a list of rows, so the response maps straight onto a downstream record
without any string parsing.
"""

import json
import os
import sys

from dotenv import load_dotenv

from extract import extract_agreement

load_dotenv()


def to_procurement_record(answer: dict) -> dict:
    vendor = answer.get("vendor", {})
    schedule = answer.get("delivery_schedule", [])

    return {
        "vendor_name": vendor.get("legal_name"),
        "vendor_country": vendor.get("country"),
        "vendor_contact": vendor.get("contact_person"),
        "vendor_email": vendor.get("email"),
        "payment_terms": answer.get("payment_terms"),
        "effective_date": answer.get("agreement_effective_date"),
        "milestones": [
            {
                "phase": row.get("phase"),
                "due": row.get("delivery_date"),
                "destination": row.get("destination"),
                "status": row.get("status"),
            }
            for row in schedule
        ],
    }


if __name__ == "__main__":
    file_id = os.getenv("AGREEMENT_FILE_ID")

    if not file_id:
        sys.exit(
            "AGREEMENT_FILE_ID is not set. Copy .env.example to .env and add "
            "the file ID of the supplier agreement you uploaded to Box."
        )

    answer = extract_agreement(file_id)
    print("Raw extraction:")
    print(json.dumps(answer, indent=2))

    record = to_procurement_record(answer)
    print("\nProcurement record:")
    print(json.dumps(record, indent=2))
