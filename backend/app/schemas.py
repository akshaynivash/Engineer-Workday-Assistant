from pydantic import BaseModel, Field


class PartSummary(BaseModel):
    id: str = Field(..., alias="ID")
    description: str = Field(..., alias="DESCRIPTION")
    application: str = Field(..., alias="Application")
    fuse_type: str = Field(..., alias="Attribut1")

    model_config = {"populate_by_name": True}


class PartFacets(BaseModel):
    applications: list[str]
    fuse_types: list[str]


class PartDetail(PartSummary):
    rated_current_a: str = Field(..., alias="Rated Current (A)")
    rated_voltage_v: str = Field(..., alias="Rated Voltage (V)")
    rated_voltage_vdc: str = Field(..., alias="Rated Voltage (VDC)")
    rated_breaking_capacity_a: str = Field(..., alias="Rated Breaking Capacity (A)")
    mounting: str = Field(..., alias="Mounting")


class ExplainRequest(BaseModel):
    use_ai: bool = False
    alternative_id: str | None = None


class ExplainResponse(BaseModel):
    explanation: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)


class ChatResponse(BaseModel):
    response: str


class TaskCreate(BaseModel):
    task: str = Field(..., min_length=1)
    answer: str = Field(..., min_length=1)
    day: str | None = None


class TaskCreateResponse(BaseModel):
    message: str


class ErrorResponse(BaseModel):
    detail: str
