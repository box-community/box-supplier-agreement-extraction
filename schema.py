"""Extraction schema for a supplier agreement.

Two complex field types do the heavy lifting here:

- ``struct`` returns a single nested JSON object. Use it for values that
  belong together, such as a vendor's legal name, address, and contacts.
- ``table`` returns an array of objects sharing one schema. Use it for
  repeating rows, such as delivery milestones or line items.

Every complex field needs a ``fields`` array describing its sub-fields.
Sub-fields accept scalar types only - nesting a ``struct`` or ``table``
inside another complex field is not supported.
"""

from box_sdk_gen import CreateAiExtractStructuredFields

EXTRACTION_FIELDS = [
    CreateAiExtractStructuredFields(
        key="agreement_effective_date",
        display_name="Effective date",
        type="date",
        prompt="The date the agreement takes effect.",
    ),
    CreateAiExtractStructuredFields(
        key="payment_terms",
        display_name="Payment terms",
        type="string",
        prompt="The payment terms, for example Net 30.",
    ),
    CreateAiExtractStructuredFields(
        key="vendor",
        display_name="Vendor",
        type="struct",
        prompt="The vendor or supplier issuing the agreement.",
        fields=[
            CreateAiExtractStructuredFields(
                key="legal_name", type="string", display_name="Legal name"
            ),
            CreateAiExtractStructuredFields(
                key="address", type="string", display_name="Address"
            ),
            CreateAiExtractStructuredFields(
                key="country", type="string", display_name="Country"
            ),
            CreateAiExtractStructuredFields(
                key="contact_person", type="string", display_name="Contact person"
            ),
            CreateAiExtractStructuredFields(
                key="email", type="string", display_name="Email"
            ),
            CreateAiExtractStructuredFields(
                key="phone", type="string", display_name="Phone"
            ),
        ],
    ),
    CreateAiExtractStructuredFields(
        key="delivery_schedule",
        display_name="Delivery schedule",
        type="table",
        prompt="Each delivery milestone defined in the agreement.",
        fields=[
            CreateAiExtractStructuredFields(
                key="phase", type="string", display_name="Phase"
            ),
            CreateAiExtractStructuredFields(
                key="items", type="string", display_name="Items"
            ),
            CreateAiExtractStructuredFields(
                key="delivery_date", type="date", display_name="Delivery date"
            ),
            CreateAiExtractStructuredFields(
                key="destination", type="string", display_name="Destination"
            ),
            CreateAiExtractStructuredFields(
                key="status", type="string", display_name="Status"
            ),
        ],
    ),
]
