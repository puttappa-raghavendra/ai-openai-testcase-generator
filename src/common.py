
from langchain_core.pydantic_v1 import BaseModel, Field

class APISummaryOutput(BaseModel):
    """API path input to extract the API spec"""
    path: str = Field(..., description="The OpenAPI spec for the API Endpoint")
    method: list[str] = Field(..., description="The HTTP method for the API Endpoint")
    

class AcceptenceCriteriaFormat(BaseModel):
    """Acceptence Criteria Output"""
    scenario: str = Field(..., description="The acceptence criteria scenario")
    given: str = Field(..., description="Initial context or state of the system or api resource")
    when: str = Field(..., description="Action that is performed")
    then: str = Field(..., description="Expected outcome of the action")
    
class ListAcceptenceCriteriaFormat(BaseModel):
    """List of Acceptence Criteria Output"""
    acceptence_criteria: list[AcceptenceCriteriaFormat] = Field(..., description="List of acceptence criterias")
   
    