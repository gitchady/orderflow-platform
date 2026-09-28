from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.service import PaymentService


def get_payment_service(
    db: Session = Depends(get_db),
) -> PaymentService:
    return PaymentService(db)
