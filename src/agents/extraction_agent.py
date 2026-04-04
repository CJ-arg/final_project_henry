from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from src.models import ContractChangeOutput
from dotenv import load_dotenv

# Load enviroments variables
load_dotenv()   

class ExtractionAgent:
    """
    Agent responsible for identifying and extracting specific legal changes
    between the original contract and the amendment.
    """
    def __init__(self):
        # We use structured_output to ensure the response matches our Pydantic model
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.0)
        self.structured_llm = self.llm.with_structured_output(ContractChangeOutput)
        
    def extract_diff(self, original_text: str, amendment_text: str, structural_map: str, langfuse_handler=None):
        """
        Identifies additions, deletions, and modifications based on the context.
        """
        system_prompt = (
            "You are a Senior Legal Auditor. Your goal is to identify exact changes in a contract amendment. "
            "Use the provided 'Structural Map' to navigate the documents accurately. "
            "Focus on finding: \n"
            "1. Additions (new clauses, sections, articles or terms)\n"
            "2. Deletions (removed clauses, sections, articles or terms)\n"
            "3. Modifications (changes in pricing, dates, obligations or any relevant detail).\n\n"
            "Output must be a strictly validated JSON following the ContractChangeOutput schema."
            "Output must be in spanish after the english translation."
        )
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", (
                "STRUCTURAL MAP:\n{map}\n\n"
                "ORIGINAL TEXT:\n{original}\n\n"
                "AMENDMENT TEXT:\n{amendment}"
            ))
        ])
        
        # Chain execution
        chain = prompt | self.structured_llm
        
        config = {"callbacks": [langfuse_handler]} if langfuse_handler else {}
        return chain.invoke({
            "map": structural_map,
            "original": original_text,
            "amendment": amendment_text
        }, config=config)
