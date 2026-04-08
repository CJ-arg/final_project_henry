from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

# Load enviroments variables
load_dotenv()       

class ContextualizationAgent:
    """
    Agent responsible for structural analysis and mapping between the original
    contract and its amendments.
    """
    def __init__(self):
        # Using GPT-4o for high-reasoning structural analysis
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.0)
    def analyze(self, original_text: str, amendments_text: str, run_name="contextualization_agent", langfuse_handler=None):
        """
        Creates comparative map of the document structures.
        """ 
        system_prompt = (
            "You are a Senior Legal Analyst who pays attention to the details specialized in contracts and amendments analysis."
            "Your task is to create a comparative map of the structure of two documents an original and its amendment."
            "Identify which sections of the original contract are being referenced in the amendment"
            "and describe the general purpose of each block."
            "Do NOT extract specific changes yet; focus only on the structural correspondence."
        ) 
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", "ORIGINAL CONTRACT:\n{original}\n\nAMENDMENT:\n{amendment}")
            ])
        # Define the chain
        chain = prompt | self.llm

        # Execute analysis
        config = {"callbacks": [langfuse_handler], "run_name": run_name} if langfuse_handler else {"run_name": run_name}
        
        # Simple try-except retry logic
        import time
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = chain.invoke({
                    "original": original_text,
                    "amendment": amendments_text
                }, config=config)
                return response.content
            except Exception as e:
                print(f"[ContextualizationAgent] Error en intento {attempt + 1}/{max_retries}: {e}")
                if attempt == max_retries - 1:
                    print("[ContextualizationAgent] Fallo definitivo tras reintentos.")
                    raise e
                time.sleep(2)