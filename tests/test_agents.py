"""
Tests for the two specialized agents.
All LLM calls are mocked to avoid API consumption.
"""
import pytest
from unittest.mock import patch, MagicMock
from src.agents.contextualization_agent import ContextualizationAgent
from src.agents.extraction_agent import ExtractionAgent
from src.models import ContractChangeOutput


# --- Sample data for tests ---
SAMPLE_ORIGINAL = "CLÁUSULA PRIMERA: El plazo del contrato es de 2 años."
SAMPLE_AMENDMENT = "CLÁUSULA PRIMERA: El plazo del contrato es de 3 años."
SAMPLE_STRUCTURAL_MAP = "La Cláusula PRIMERA del original corresponde a la Cláusula PRIMERA de la adenda. Tema: Duración."


class TestContextualizationAgent:
    """Tests for Agent 1: ContextualizationAgent."""

    @patch("src.agents.contextualization_agent.ChatOpenAI")
    def test_analyze_returns_string(self, mock_llm_class):
        """The analyze method should return a string (structural map)."""
        mock_model = MagicMock()
        mock_model.invoke.return_value = MagicMock(content=SAMPLE_STRUCTURAL_MAP)
        
        # Mock the pipe operator (prompt | llm) to return a chain that uses our mock
        mock_llm_class.return_value = mock_model

        agent = ContextualizationAgent()
        agent.llm = mock_model

        # Build a mock chain
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = MagicMock(content=SAMPLE_STRUCTURAL_MAP)

        with patch.object(agent, 'analyze', wraps=agent.analyze):
            # Patch the chain creation
            with patch("src.agents.contextualization_agent.ChatPromptTemplate") as mock_prompt:
                mock_prompt.from_messages.return_value.__or__ = MagicMock(return_value=mock_chain)

                result = agent.analyze(SAMPLE_ORIGINAL, SAMPLE_AMENDMENT)

        assert isinstance(result, str)
        assert len(result) > 0

    @patch("src.agents.contextualization_agent.ChatOpenAI")
    def test_analyze_retries_on_failure(self, mock_llm_class):
        """Should retry when the LLM call fails."""
        mock_model = MagicMock()
        mock_llm_class.return_value = mock_model

        agent = ContextualizationAgent()

        mock_chain = MagicMock()
        mock_chain.invoke.side_effect = [
            Exception("Timeout"),
            MagicMock(content="Mapa generado tras reintento.")
        ]

        with patch("src.agents.contextualization_agent.ChatPromptTemplate") as mock_prompt:
            mock_prompt.from_messages.return_value.__or__ = MagicMock(return_value=mock_chain)
            result = agent.analyze(SAMPLE_ORIGINAL, SAMPLE_AMENDMENT)

        assert result == "Mapa generado tras reintento."
        assert mock_chain.invoke.call_count == 2


class TestExtractionAgent:
    """Tests for Agent 2: ExtractionAgent."""

    @patch("src.agents.extraction_agent.ChatOpenAI")
    def test_extract_diff_returns_pydantic_model(self, mock_llm_class):
        """The extract_diff method should return a ContractChangeOutput instance."""
        expected_output = ContractChangeOutput(
            sections_changed=["PRIMERA"],
            topics_touched=["Duración"],
            summary_of_changes="El plazo se extendió de 2 a 3 años."
        )

        mock_model = MagicMock()
        mock_structured = MagicMock()
        mock_model.with_structured_output.return_value = mock_structured
        mock_llm_class.return_value = mock_model

        agent = ExtractionAgent()
        agent.structured_llm = mock_structured

        mock_chain = MagicMock()
        mock_chain.invoke.return_value = expected_output

        with patch("src.agents.extraction_agent.ChatPromptTemplate") as mock_prompt:
            mock_prompt.from_messages.return_value.__or__ = MagicMock(return_value=mock_chain)
            result = agent.extract_diff(
                SAMPLE_ORIGINAL, SAMPLE_AMENDMENT, SAMPLE_STRUCTURAL_MAP
            )

        assert isinstance(result, ContractChangeOutput)
        assert "PRIMERA" in result.sections_changed
        assert "Duración" in result.topics_touched

    @patch("src.agents.extraction_agent.ChatOpenAI")    
    def test_extract_diff_retries_on_failure(self, mock_llm_class):
        """Should retry when the LLM call fails."""
        expected_output = ContractChangeOutput(
            sections_changed=["PRIMERA"],
            topics_touched=["Duración"],
            summary_of_changes="Recuperado tras reintento."
        )

        mock_model = MagicMock()
        mock_structured = MagicMock()
        mock_model.with_structured_output.return_value = mock_structured
        mock_llm_class.return_value = mock_model

        agent = ExtractionAgent()
        agent.structured_llm = mock_structured

        mock_chain = MagicMock()
        mock_chain.invoke.side_effect = [
            Exception("Rate limit exceeded"),
            expected_output
        ]

        with patch("src.agents.extraction_agent.ChatPromptTemplate") as mock_prompt:
            mock_prompt.from_messages.return_value.__or__ = MagicMock(return_value=mock_chain)
            result = agent.extract_diff(
                SAMPLE_ORIGINAL, SAMPLE_AMENDMENT, SAMPLE_STRUCTURAL_MAP
            )

        assert isinstance(result, ContractChangeOutput)
        assert mock_chain.invoke.call_count == 2
