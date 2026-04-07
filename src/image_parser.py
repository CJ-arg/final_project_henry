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

def parse_contract_image(image_path, langfuse_handler=None):
   """
   Sends the image to GPT-4o Vision to extract the full text while mainteining the exact numbering, clause titles, and layout structure."  
   """
   # Initialize the multimodal model
   model = ChatOpenAI(model="gpt-4o")

   # Encode image to base64
   base_64_image = encode_image(image_path)

   system_instructions = (
        "You are a highly accurate Document Digitization Specialist. "
        "Your task is to transcribe the following legal document image into raw text for archival purposes. "
        "Maintain the exact numbering, clause titles, and layout. "
        "If you see signatures or sensitive handwritten data, just represent them as [Signature] or [Handwritten text]. "
        "Do not omit any printed text."
    )

   #Create the multimodal message payload
   message = HumanMessage(
      content=[
         {
            "type": "text",
            "text": system_instructions
         },
         {
            "type": "image_url",
            "image_url": {
               "url": f"data:image/jpeg;base64,{base_64_image}",
               "detail": "high" #High detail is required to capture small text and precise numeric changes
            }
         }
      ]
   )  
   # Invoke the model and return the estacted text content
   config = {"callbacks": [langfuse_handler]} if langfuse_handler else {}
   
   # Invoke the model passing the configuration for Langfuse
   response = model.invoke([message], config=config)
   return response.content


