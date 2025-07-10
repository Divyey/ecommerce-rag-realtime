from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class UpdateLogBase(BaseModel):
    product_id: str
    change_type: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    changed_by: int

class UpdateLogOut(UpdateLogBase):
    id: int
    changed_at: datetime

    model_config = ConfigDict(from_attributes=True)
