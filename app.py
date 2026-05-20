from fastapi import Body, FastAPI
from pydantic import BaseModel

from main import credit_scoring

app = FastAPI()


class ScoringRequest(BaseModel):
    income: int
    loan_amount: int


@app.post("/api/v1/scoring")
def scoring(data: ScoringRequest = Body(...)):
    decision = credit_scoring(data.income, data.loan_amount)
    return {"status": decision}
