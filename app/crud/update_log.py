from sqlalchemy.orm import Session
from app.models.update_log import UpdateLog
from typing import List

def create_update_log(db: Session, log_data: dict) -> UpdateLog:
    log = UpdateLog(**log_data)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log

def get_logs_for_product(db: Session, product_id: str) -> List[UpdateLog]:
    return db.query(UpdateLog).filter(UpdateLog.product_id == product_id).order_by(UpdateLog.changed_at.desc()).all()
