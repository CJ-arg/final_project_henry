import base64
import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

# Load enviroments variables
load_dotenv()

def encode_image(image_path):
   """Reads a local image file and encodes it to base64 string"""
   with open(image_path, "rb") as image_file:
      return base64.b64encode(image_file.read()).decode('utf-8')

def parse_contract_image(image_paths, run_name="Contract_OCR_Vision", langfuse_handler=None):
   """
   Sends the image to GPT-4o Vision to extract the full text while mainteining the exact numbering, clause titles, and layout structure."  
   """
   # Initialize the multimodal model
   model = ChatOpenAI(model="gpt-4o", timeout=120)

   # Handle single image path or list of paths
   if isinstance(image_paths, str):
        image_paths = [image_paths]

   system_instructions = (
        "You are a highly accurate Document Digitization Specialist. "
        "Your task is to transcribe the following legal document image into raw text for archival purposes. "
        "Maintain the exact numbering, clause titles, and layout. "
        "If you see signatures or sensitive handwritten data, just represent them as [Signature] or [Handwritten text]. "
        "Do not omit any printed text."
    )

   content = [{"type": "text", "text": system_instructions}]

    # Encode each image and add it to the message payload
   for path in image_paths:
        base_64_image = encode_image(path)
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base_64_image}",
                "detail": "high"
            }
        })

    # Create the multimodal message payload
   message = HumanMessage(content=content)

    # Configure Langfuse with a specific run_name for better observability
   config = {
        "callbacks": [langfuse_handler],
        "run_name": run_name
    } if langfuse_handler else {"run_name": run_name}
    
    # Try-except retry logic
   import time
   max_retries = 3
   for attempt in range(max_retries):
       try:
           # Invoke the model passing the configuration for Langfuse
           response = model.invoke([message], config=config)
           return response.content
       except Exception as e:
           print(f"[ImageParser ({config.get('run_name', 'Vision')})] Error en intento {attempt + 1}/{max_retries}: {e}")
           if attempt == max_retries - 1:
               print(f"[ImageParser] Fallo definitivo tras reintentos.")
               raise e
           time.sleep(2)



