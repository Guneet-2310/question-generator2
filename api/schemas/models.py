from pydantic import BaseModel, Field
from typing import Literal

class QuestionRequest(BaseModel):
    num_mcqs: int = Field(3, ge=1, le=10)
    num_shortans: int = Field(2, ge=1, le=5)
    difficulty: Literal["Easy", "Medium", "Hard"] = "Easy"