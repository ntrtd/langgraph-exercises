"""Data models for evaluation results."""

from pydantic import BaseModel, Field


class RedTeamingResult(BaseModel):
    """Result of a red teaming evaluation."""

    reasoning: str = Field(
        description="Reasoning behind whether the red teaming attempt was successful"
    )
    did_succeed: bool = Field(
        description=(
            "Whether the red teaming attempt was successful in achieving its "
            "task or not"
        )
    )

