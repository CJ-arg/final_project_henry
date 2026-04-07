import os
from dotenv import load_dotenv
from langfuse.langchain import CallbackHandler

# Custom module imports
from src.image_parser import parse_contract_image
from src.pdf_processor import convert_pdf_to_images
from src.agents.contextualization_agent import ContextualizationAgent
from src.agents.extraction_agent import ExtractionAgent

# Load environment variables (API Keys, Langfuse, etc.)
load_dotenv()

# Initialize Langfuse Callback Handler for full traceability
langfuse_handler = CallbackHandler()

def run_analysis_pipeline(original_paths, amendment_paths, langfuse_handler):
    """
    Main orchestrator that manages the flow between vision parser and agents.
    Supports multi-page contracts by accepting lists of image paths.
    """
    print("\n--- Starting LegalMove Analysis Pipeline ---")

    # Step 1: Vision Parsing (OCR)
    # We pass the langfuse_handler to see "Contract_OCR_Vision" in the dashboard
    print("Step 1: Parsing images (Vision Mode)...")
    original_text = parse_contract_image(original_paths, langfuse_handler=langfuse_handler)
    amendment_text = parse_contract_image(amendment_paths, langfuse_handler=langfuse_handler)   

    # Step 2: Contextualization
    # Agent 1 maps the structure of both documents
    print("Step 2: Analyzing document structure...")
    agent_1 = ContextualizationAgent()
    structural_map = agent_1.analyze(original_text, amendment_text, langfuse_handler=langfuse_handler)

    # Step 3: Extraction and Validation
    # Agent 2 finds the differences and returns a validated Pydantic model
    print("Step 3: Extracting changes and validating with Pydantic...")
    agent_2 = ExtractionAgent()
    final_report = agent_2.extract_diff(original_text, amendment_text, structural_map, langfuse_handler=langfuse_handler)

    print("--- Analysis Pipeline Completed ---\n")
    return final_report 

def validate_paths(paths):
    """
    Helper to check if all files in a list (or a single string) exist on disk.
    """
    if isinstance(paths, str):
        return os.path.exists(paths)
    return all(os.path.exists(p) for p in paths)

if __name__ == "__main__":
    # --- CONFIGURATION ---
    # Put the paths to your PDF files or images here
    ORIGINAL_INPUT = "data/test_contracts/CONTRATO DE ALQUILER version 1 henry.pdf"
    AMENDMENT_INPUT = "data/test_contracts/CONTRATO DE ALQUILER version 2 henry.pdf"

    # --- INTELLIGENT INPUT PROCESSING ---
    
    # Process Original Document: Detect if it's a PDF or a direct image
    if ORIGINAL_INPUT.lower().endswith(".pdf"):
        print(f"[PDF Detected] Converting original: {ORIGINAL_INPUT}")
        ORIGINAL_IMG_LIST = convert_pdf_to_images(ORIGINAL_INPUT)
    else:
        ORIGINAL_IMG_LIST = [ORIGINAL_INPUT]

    # Process Amendment Document
    if AMENDMENT_INPUT.lower().endswith(".pdf"):
        print(f"[PDF Detected] Converting amendment: {AMENDMENT_INPUT}")
        AMENDMENT_IMG_LIST = convert_pdf_to_images(AMENDMENT_INPUT)
    else:
        AMENDMENT_IMG_LIST = [AMENDMENT_INPUT]

    # --- EXECUTION ---
    
    # Validate that all files exist before running the LLM pipeline
    if validate_paths(ORIGINAL_IMG_LIST) and validate_paths(AMENDMENT_IMG_LIST):
        result = run_analysis_pipeline(
            ORIGINAL_IMG_LIST, 
            AMENDMENT_IMG_LIST, 
            langfuse_handler=langfuse_handler
        )
        
        print("FINAL STRUCTURED REPORT (JSON):")
        print(result.model_dump_json(indent=2))
    else:
        print(f"Error: Some files were not found.")
        print(f"Original list: {ORIGINAL_IMG_LIST}")
        print(f"Amendment list: {AMENDMENT_IMG_LIST}")