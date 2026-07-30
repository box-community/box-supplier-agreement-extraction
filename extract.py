"""Call Box AI structured extraction against a supplier agreement."""

from box_sdk_gen import AiItemBase, AiAgentReference, AiAgentReferenceTypeField

from box_client import get_box_client
from schema import EXTRACTION_FIELDS


def extract_agreement(file_id: str) -> dict:
    """Extract the schema in ``schema.py`` from one Box file.

    The Enhanced Extract Agent is a predefined Box AI agent referenced by
    ID. It is optional, but it improves accuracy on the nested and
    repeating fields this schema relies on.
    """
    client = get_box_client()

    response = client.ai.create_ai_extract_structured(
        items=[AiItemBase(id=file_id)],
        fields=EXTRACTION_FIELDS,
        ai_agent=AiAgentReference(
            id="enhanced_extract_agent",
            type=AiAgentReferenceTypeField.AI_AGENT_ID,
        ),
    )

    return response.to_dict()["answer"]
