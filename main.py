import os
from dotenv import load_dotenv
from langfuse.callback import CallbackHandler
from src.image_parser import parse_contract_image
from src.agents.contextualization_agent import ContextualizationAgent
from src.agents.extraction_agent import ExtractionAgent

# Load environment variables and Langfuse keys
load_dotenv()

# Initialize Langfuse Callback Handler for traceability

langfuse_handler = CallbackHandler(
    api_key=os.environ.get("LANGFUSE_API_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_BASE_URL")
)   

def run_analysis_pipeline(original_path, amendment_path, langfuse_handler):
    """
    Main orchestator that manages the flow between vision parser and agentes.
    It uses Langfuse to trace ehe entire process.
    """
    print("--- Starting LegalMove Analysis Pipeline --- ")

    # Step 1 Vision Parsing
    # We execute this twice as required by the instructions
    print("Step 1 Parsing images...")
    original_text = parse_contract_image(original_path)
    amendment_text = parse_contract_image(amendment_path)   

    # Step 2 Contextualization
    print("Step 2 Analyzing document Structure...")
    agent_1 = ContextualizationAgent()
    structural_map = agent_1.analyze(original_text, amendment_text)

    # Step 3 Extraction and Validation
    print("Step 3 Extracting changes and validating with LLM and Pydantic model...")
    agent_2 = ExtractionAgent()
    # The oputput is automatically validated by the Pydantic model defined in models
    final_report = agent_2.extract_diff(original_text, amendment_text, structural_map)

    print("--- Analysis Pipeline Completed ---")
    return final_report 

if __name__ == "__main__":
    # Test paths - Ensure these images exist in your data/test_contracts folder
    ORIGINAL_IMG = "data\test_contracts/original.jpg"
    AMENDMENT_IMG = "data\test_contracts/amendment.jpg"
    run_analysis_pipeline(ORIGINAL_IMG, AMENDMENT_IMG)

    if os.path.exists(ORIGINAL_IMG) and os.path.exists(AMENDMENT_IMG):
        # We pass the langfuse_handler to ensure every step is recorded
        result = run_analysis_pipeline(ORIGINAL_IMG, AMENDMENT_IMG, langfuse_handler=langfuse_handler)
        print("/n FINAL STRUCTURED REPORT (JSON): ")
        print(result.model_dump_json(indent=2))
    else:
        print(f"Error: Images not found at {ORIGINAL_IMG} or {AMENDMENT_IMG}")