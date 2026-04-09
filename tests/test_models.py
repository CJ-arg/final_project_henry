"""
Tests for the Pydantic model ContractChangeOutput.
Validates that the schema enforces correct types and required fields.
"""
import pytest
from pydantic import ValidationError
from src.models import ContractChangeOutput


class TestContractChangeOutput:
    """Tests for the ContractChangeOutput Pydantic model."""

    def test_valid_output_creation(self):
        """A valid instance should be created without errors."""
        output = ContractChangeOutput(
            sections_changed=["CUARTA", "QUINTA"],
            topics_touched=["Duración", "Precios"],
            summary_of_changes="Se modificó la cláusula CUARTA extendiendo el plazo."
        )
        assert output.sections_changed == ["CUARTA", "QUINTA"]
        assert output.topics_touched == ["Duración", "Precios"]
        assert "CUARTA" in output.summary_of_changes

    def test_model_dump_json(self):
        """model_dump_json() should return a valid JSON string."""
        output = ContractChangeOutput(
            sections_changed=["Cláusula 3"],
            topics_touched=["Jurisdicción"],
            summary_of_changes="Cambio de jurisdicción de Buenos Aires a La Plata."
        )
        json_str = output.model_dump_json(indent=2)
        assert '"sections_changed"' in json_str
        assert '"topics_touched"' in json_str
        assert '"summary_of_changes"' in json_str

    def test_missing_sections_changed_raises_error(self):
        """Omitting a required field should raise ValidationError."""
        with pytest.raises(ValidationError):
            ContractChangeOutput(
                topics_touched=["Precios"],
                summary_of_changes="Resumen de cambios."
            )

    def test_missing_topics_touched_raises_error(self):
        """Omitting topics_touched should raise ValidationError."""
        with pytest.raises(ValidationError):
            ContractChangeOutput(
                sections_changed=["CUARTA"],
                summary_of_changes="Resumen de cambios."
            )

    def test_missing_summary_raises_error(self):
        """Omitting summary_of_changes should raise ValidationError."""
        with pytest.raises(ValidationError):
            ContractChangeOutput(
                sections_changed=["CUARTA"],
                topics_touched=["Precios"]
            )

    def test_wrong_type_sections_changed(self):
        """sections_changed must be a list, not a plain string."""
        with pytest.raises(ValidationError):
            ContractChangeOutput(
                sections_changed="CUARTA",  # Should be a list
                topics_touched=["Precios"],
                summary_of_changes="Resumen."
            )

    def test_wrong_type_summary(self):
        """summary_of_changes must be a string, not a list."""
        with pytest.raises(ValidationError):
            ContractChangeOutput(
                sections_changed=["CUARTA"],
                topics_touched=["Precios"],
                summary_of_changes=["Esto", "es", "una", "lista"]  # Should be str
            )

    def test_empty_lists_are_valid(self):
        """Empty lists are technically valid (no changes detected)."""
        output = ContractChangeOutput(
            sections_changed=[],
            topics_touched=[],
            summary_of_changes="No se detectaron cambios."
        )
        assert output.sections_changed == []
        assert output.topics_touched == []
