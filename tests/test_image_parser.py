"""
Tests for image_parser module.
Tests encoding logic and input normalization without calling the OpenAI API.
"""
import os
import base64
import pytest
from unittest.mock import patch, MagicMock
from src.image_parser import encode_image, parse_contract_image


class TestEncodeImage:
    """Tests for the encode_image() utility function."""

    def test_encode_existing_image(self):
        """Should return a valid base64 string for an existing image."""
        # Use one of the test contract images
        test_image = "data/test_contracts/original.jpg"
        if not os.path.exists(test_image):
            pytest.skip("Test image not found")
        
        result = encode_image(test_image)
        
        # Verify it's a valid base64 string (can be decoded without error)
        decoded = base64.b64decode(result)
        assert len(decoded) > 0

    def test_encode_nonexistent_image_raises_error(self):
        """Should raise FileNotFoundError for a non-existent file."""
        with pytest.raises(FileNotFoundError):
            encode_image("data/test_contracts/nonexistent_file.jpg")


class TestParseContractImage:
    """Tests for parse_contract_image() with mocked LLM calls."""

    @patch("src.image_parser.ChatOpenAI")
    @patch("src.image_parser.encode_image")
    def test_accepts_single_string_path(self, mock_encode, mock_llm_class):
        """Should normalize a single string path into a list internally."""
        mock_encode.return_value = "fake_base64_data"
        mock_model = MagicMock()
        mock_model.invoke.return_value = MagicMock(content="Texto extraído del contrato.")
        mock_llm_class.return_value = mock_model

        result = parse_contract_image("data/test_contracts/original.jpg")
        
        assert result == "Texto extraído del contrato."
        mock_encode.assert_called_once_with("data/test_contracts/original.jpg")

    @patch("src.image_parser.ChatOpenAI")
    @patch("src.image_parser.encode_image")
    def test_accepts_list_of_paths(self, mock_encode, mock_llm_class):
        """Should accept a list of image paths for multi-page documents."""
        mock_encode.return_value = "fake_base64_data"
        mock_model = MagicMock()
        mock_model.invoke.return_value = MagicMock(content="Texto de múltiples páginas.")
        mock_llm_class.return_value = mock_model

        result = parse_contract_image(["page1.jpg", "page2.jpg"])
        
        assert result == "Texto de múltiples páginas."
        assert mock_encode.call_count == 2

    @patch("src.image_parser.ChatOpenAI")
    @patch("src.image_parser.encode_image")
    def test_retries_on_api_failure(self, mock_encode, mock_llm_class):
        """Should retry up to 3 times when the API call fails."""
        mock_encode.return_value = "fake_base64_data"
        mock_model = MagicMock()
        # First call fails, second succeeds
        mock_model.invoke.side_effect = [
            Exception("API Timeout"),
            MagicMock(content="Texto recuperado tras reintento.")
        ]
        mock_llm_class.return_value = mock_model

        result = parse_contract_image("test.jpg")
        
        assert result == "Texto recuperado tras reintento."
        assert mock_model.invoke.call_count == 2

    @patch("src.image_parser.ChatOpenAI")
    @patch("src.image_parser.encode_image")
    def test_raises_after_max_retries(self, mock_encode, mock_llm_class):
        """Should raise the exception after exhausting all retries."""
        mock_encode.return_value = "fake_base64_data"
        mock_model = MagicMock()
        mock_model.invoke.side_effect = Exception("Persistent API Error")
        mock_llm_class.return_value = mock_model

        with pytest.raises(Exception, match="Persistent API Error"):
            parse_contract_image("test.jpg")
        
        assert mock_model.invoke.call_count == 3
