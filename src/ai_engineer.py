# 1st. execute the request and get collect the API and api specification 
# let define the planner class 
# define the predefined plan 

# 2nd. execute the request to collect the AC 

from typing import Dict, TypedDict, Optional, Annotated, List, Tuple
import operator
from langgraph.graph import StateGraph, END


class OpenAPITestState(TypedDict):
    question: Optional[str] = None
    api_path: Optional[str] = None
    method: Optional[list[str]] = None
    specification: Optional[Dict] = None
    acceptence_criteria: Optional[Dict] = None

workflow = StateGraph(OpenAPITestState)

# Define the tools 
# tool is used to extract the API from question and method
def extract_api_method(state: OpenAPITestState) -> OpenAPITestState:
    
    print(f"Extracting API method from the question: {state['question']}")
    from api_spec_summary import get_api_details
    from common import APISummaryOutput
    api_output = get_api_details(state["question"])
    # use LLm to extract API from LLM 
    state["api_path"] = api_output.path
    state["method"] = api_output.method
    return state

def extract_api_specification(state: OpenAPITestState) -> OpenAPITestState:
    print(f"Extracting API specification from the API path: {state['api_path']}")
    from api_spec_extractor import fetch_api_openapi_specification
    api_path = state["api_path"]
    methods = state["method"]
    if state["specification"] is None:
        state["specification"] = {}
    specification = state["specification"]
    for method in methods:
        specification[method] = fetch_api_openapi_specification(api_path, method)
        
    state["specification"] = specification
    return state

def build_accepten_criteria(state: OpenAPITestState) -> OpenAPITestState:
    print(f"Building acceptence criteria for the API: {state['api_path']}")
    # simple method call to build the acceptence criteria
    # pass the API specification to build the list of acceptence criteria
    from api_ac_generator import api_acceptence_criteria_generator
    from common import AcceptenceCriteriaFormat, ListAcceptenceCriteriaFormat
    specifications = state["specification"]
    
    ac_list = {}
    for key, value in specifications.items():
        list_of_ac_obj = api_acceptence_criteria_generator(value)
        ac_list[key] = list_of_ac_obj
    state["acceptence_criteria"] = ac_list
    return state

def build_test_cases(state: OpenAPITestState) -> OpenAPITestState:
    print(f"Building test cases for the API: {state['api_path']}")
    # simple method call to build the test cases
    # pass the acceptence criteria to build the test cases
    acceptence_criteria = state["acceptence_criteria"]
    state["test_cases"] = ["Test Case 1", "Test Case 2"]
    return state


workflow.add_node("extract_api_method", extract_api_method)
workflow.add_node("extract_api_specification", extract_api_specification)
workflow.add_node("build_accepten_criteria", build_accepten_criteria)
workflow.add_node("build_test_cases", build_test_cases)

workflow.add_edge("extract_api_method", "extract_api_specification")
workflow.add_edge("extract_api_specification", "build_accepten_criteria")
workflow.add_edge("build_accepten_criteria", "build_test_cases")
workflow.add_edge("build_test_cases", END)

workflow.set_entry_point("extract_api_method")

app = workflow.compile()
inputs = {"question": "Generate acceptence criteria for the virtual machines api"}
result = app.invoke(inputs)
acceptence_criteria = result["acceptence_criteria"]
for key, value in acceptence_criteria.items():
    for ac_obj in value:
        for ac in ac_obj.acceptence_criteria:
            # build the test cases
            print( ac.scenario )
            print( ac.given )
            print( ac.when )
            print(ac.then)