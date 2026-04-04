from pydantic import BaseModel, Field
from typing import List

class ContractChangeOutput(BaseModel):
    """ Validated output schema for the contract chande analysis report
        This model ensures the AI provides structured and consistent data.
    """

    sections_changed: List[str] = Field(
        description="List of exact clause identifieers or section numbers that were modified (e.g., 'Section 3', 'Clause 4.1')."
    )
    topics_touched: List[str] = Field(
        description="Legal or commercial categories affected by the changes, such as 'Pricing', 'Support', 'Duration', or 'Intellectual Property'."
    )
    summary_of_changes: str = Field(
        description="Detailed professional narrative describing exactly what changed, including old vs. new values and the legal impact"
    )