from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.update_log import UpdateLogOut
from app.crud.product import get_product
from app.crud.update_log import get_logs_for_product
from app.core.dependencies import get_db
from typing import List

router = APIRouter()

@router.get("/logs/{product_id}", response_model=List[UpdateLogOut])
def get_logs(
    product_id: str,
    db: Session = Depends(get_db),
):
    product = get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    logs = get_logs_for_product(db, product_id)
    return logs
