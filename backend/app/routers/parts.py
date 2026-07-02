from fastapi import APIRouter, HTTPException, Query
from fastapi.concurrency import run_in_threadpool

from app.data import load_parts_df
from app.schemas import ExplainRequest, ExplainResponse, PartDetail, PartFacets, PartSummary
from app.services.explanations import (
    generate_ai_explanation,
    rule_based_justification,
    rule_based_physics_explanation,
)
from app.services.filtering import find_alternative_parts_balanced

router = APIRouter(prefix="/api/parts", tags=["parts"])

VALID_TIERS = {"Tier 1", "Tier 2", "Tier 3", "Tier 4", "Tier 5"}


def _get_part_or_404(part_id: str):
    df = load_parts_df()
    rows = df[df["ID"] == part_id]
    if rows.empty:
        raise HTTPException(status_code=404, detail=f"Part '{part_id}' not found")
    return rows.iloc[0]


async def _ai_explanation_or_503(prompt: str) -> str:
    try:
        return await run_in_threadpool(generate_ai_explanation, prompt)
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"AI explanations need the Phi-1.5 weights installed (run model_install.py). Details: {e}",
        ) from e


@router.get("", response_model=list[PartSummary])
def browse_parts(
    application: str | None = Query(None),
    fuse_type: str | None = Query(None),
    limit: int = Query(20, ge=1, le=200),
):
    """Browse/search the catalog -- powers "not sure which ID to try" discovery."""
    df = load_parts_df()
    if application:
        df = df[df["Application"] == application]
    if fuse_type:
        df = df[df["Attribut1"] == fuse_type]
    return [PartSummary.model_validate(row.to_dict()) for _, row in df.head(limit).iterrows()]


@router.get("/facets", response_model=PartFacets)
def get_facets():
    """Distinct filter values for the browse/search panel -- must be registered
    before /{part_id} so it isn't shadowed by the path param."""
    df = load_parts_df()
    return PartFacets(
        applications=sorted(df["Application"].dropna().unique().tolist()),
        fuse_types=sorted(df["Attribut1"].dropna().unique().tolist()),
    )


@router.get("/{part_id}", response_model=PartDetail)
def get_part(part_id: str):
    part = _get_part_or_404(part_id)
    return PartDetail.model_validate(part.to_dict())


@router.get("/{part_id}/alternatives", response_model=list[PartSummary])
def get_alternatives(part_id: str, tier: str = Query("Tier 1")):
    if tier not in VALID_TIERS:
        raise HTTPException(status_code=422, detail=f"tier must be one of {sorted(VALID_TIERS)}")
    part = _get_part_or_404(part_id)
    df = load_parts_df()
    alternatives = find_alternative_parts_balanced(part, df.copy(), relaxation_tier=tier)
    return [PartSummary.model_validate(row.to_dict()) for _, row in alternatives.iterrows()]


@router.post("/{part_id}/explain", response_model=ExplainResponse)
async def explain_part(part_id: str, payload: ExplainRequest):
    """Explains the part itself, or (if alternative_id is set) why that
    alternative is a suitable replacement for part_id."""
    part = _get_part_or_404(part_id)

    if payload.alternative_id is None:
        if payload.use_ai:
            prompt = (
                f"Explain the physics behind a {part['Attribut1']} fuse with a rated current of "
                f"{part['Rated Current (A)']}, rated voltage of {part['Rated Voltage (V)']}, and breaking "
                f"capacity of {part['Rated Breaking Capacity (A)']}. It is used in {part['Application']} applications."
            )
            explanation = await _ai_explanation_or_503(prompt)
        else:
            explanation = rule_based_physics_explanation(part["Attribut1"], part["Application"])
        return ExplainResponse(explanation=explanation)

    alternative = _get_part_or_404(payload.alternative_id)
    if payload.use_ai:
        prompt = (
            f"Explain why this alternative part with a {alternative['Attribut1']} fuse type, rated current of "
            f"{alternative['Rated Current (A)']}, rated voltage of {alternative['Rated Voltage (V)']}, and "
            f"breaking capacity of {alternative['Rated Breaking Capacity (A)']} is a suitable replacement for "
            f"the original part with a {part['Attribut1']} fuse type, rated current of {part['Rated Current (A)']}, "
            f"rated voltage of {part['Rated Voltage (V)']}, and breaking capacity of {part['Rated Breaking Capacity (A)']}. "
            f"The mounting type is {alternative['Mounting']}."
        )
        explanation = await _ai_explanation_or_503(prompt)
    else:
        explanation = rule_based_justification(
            part["Attribut1"], alternative["Attribut1"],
            part["Rated Current (A)"], alternative["Rated Current (A)"],
            part["Rated Voltage (V)"], alternative["Rated Voltage (V)"],
            part["Mounting"], alternative["Mounting"],
        )
    return ExplainResponse(explanation=explanation)
