
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

# load environment variables
from os import getenv
from dotenv import load_dotenv

load_dotenv(".env")

class ApiSummary(BaseModel):
    path: str
    method: str
    summary: str
    
def fetch_api_summary() -> list[ApiSummary]:
    """Search all APIs in the OpenAPI spec"""
    summary = get_all_apis("data/apis/openapi-specification.yaml")
    return summary

import yaml

def get_all_apis(openapi_spec_path):
    """List all avialble APIs """
    with open(openapi_spec_path, 'r') as f:
        spec_dict = yaml.safe_load(f)

    api_summaries = []

    # Get paths and operations from the spec
    paths = spec_dict.get('paths', {})

    # Iterate over each path and its operations
    for path, path_details in paths.items():
        for method, description in path_details.items():
            if type(description) is not dict:
                continue 
            summary = description.get('summary', '')
            api_summaries.append(ApiSummary(path=path, method=method.lower(), summary=summary))

    return api_summaries


from common import APISummaryOutput
    
api_summary_parser = PydanticOutputParser(pydantic_object=APISummaryOutput)
api_summary_format_instruction = api_summary_parser.get_format_instructions()

# chat prompt template
template = '''You are Test Automation Engineer and you are good in understanding Open API specifications.
For user request to generate the test or generate the acceptence criteria, just extract the API path & method. 
For API path & method, please use the provided context only. Please don't make up any API path or method on your own. 

Context:
    {api_summary_details}
Format instructions:
    {format_instructions}
User Question: 
    {question}
    
Please just use the provided context to find out the API path, method. If you can't find the details, please return None.
'''


# chatopenai model
chat_llm = ChatOpenAI(openai_api_key=getenv("OPENAI_API_KEY"))

prompt = ChatPromptTemplate.from_template(template=template, 
                                          input_args=["question", "api_summary_details"], 
                                          partial_variables={"format_instructions": api_summary_format_instruction })

llm_prompt_json_parser = prompt | chat_llm | api_summary_parser

def get_api_details(question: str) -> APISummaryOutput:
    return llm_prompt_json_parser.invoke({"question": question, "api_summary_details": fetch_api_summary() })