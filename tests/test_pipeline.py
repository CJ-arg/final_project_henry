"""
Integration test for the full analysis pipeline.
All external calls (OpenAI, Langfuse) are mocked.
"""
import pytest
from unittest.mock import patch, MagicMock
from pydantic import ValidationError
from src.models import ContractChangeOutput
from main import run_analysis_pipeline, validate_paths


class TestValidatePaths:
    """Tests for the validate_paths() helper."""

    def test_existing_file_returns_true(self):
        """Should return True for a file that exists."""
        assert validate_paths("main.py") is True

    def test_nonexistent_file_returns_false(self):
        """Should return False for a file that doesn't exist."""
        assert validate_paths("archivo_inexistente.xyz") is False

    def test_list_of_existing_files(self):
        """Should return True when all files in the list exist."""
        assert validate_paths(["main.py", "pyproject.toml"]) is True

    def test_list_with_missing_file(self):
        """Should return False if any file in the list is missing."""
        assert validate_paths(["main.py", "no_existe.txt"]) is False


class TestRunAnalysisPipeline:
    """Integration tests for the pipeline orchestrator (all LLM calls mocked)."""

    @patch("main.CallbackHandler")
    @patch("main.ExtractionAgent")
    @patch("main.ContextualizationAgent")
    @patch("main.parse_contract_image")
    def test_successful_pipeline(self, mock_parser, mock_ctx_class, mock_ext_class, mock_handler):
        """Full pipeline should return a ContractChangeOutput on success."""
        # Mock the vision parser
        mock_parser.side_effect = [
            "Texto del contrato original.",
            "Texto de la adenda."
        ]

        # Mock Agent 1 (Contextualization)
        mock_ctx = MagicMock()
        mock_ctx.analyze.return_value = "Mapa: Cláusula 1 original = Cláusula 1 adenda (Duración)."
        mock_ctx_class.return_value = mock_ctx

        # Mock Agent 2 (Extraction)
        expected = ContractChangeOutput(
            sections_changed=["PRIMERA"],
            topics_touched=["Duración"],
            summary_of_the_change="El plazo se extendió de 2 a 3 años."
        )
        mock_ext = MagicMock()
        mock_ext.extract_diff.return_value = expected
        mock_ext_class.return_value = mock_ext

        result = run_analysis_pipeline(["original.jpg"], ["amendment.jpg"])

        assert isinstance(result, ContractChangeOutput)
        assert result.sections_changed == ["PRIMERA"]
        # Verify the handoff: Agent 2 received Agent 1's map
        mock_ext.extract_diff.assert_called_once()
        call_args = mock_ext.extract_diff.call_args
        assert "Mapa:" in call_args[0][2]  # structural_map is the 3rd positional arg

    @patch("main.CallbackHandler")
    @patch("main.parse_contract_image")
    def test_pipeline_handles_validation_error(self, mock_parser, mock_handler):
        """Pipeline should return None and print error on ValidationError."""
        mock_parser.side_effect = ValidationError.from_exception_data(
            title="ContractChangeOutput",
            line_errors=[],
            input_type="python",
        )

        result = run_analysis_pipeline(["original.jpg"], ["amendment.jpg"])
        assert result is None

    @patch("main.CallbackHandler")
    @patch("main.parse_contract_image")
    def test_pipeline_handles_generic_exception(self, mock_parser, mock_handler):
        """Pipeline should return None on unexpected errors."""
        mock_parser.side_effect = Exception("Connection refused")

        result = run_analysis_pipeline(["original.jpg"], ["amendment.jpg"])
        assert result is None
