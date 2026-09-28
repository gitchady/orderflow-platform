from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI

from app.database import engine
from app.models import Base
from app.schemas import OrderCreateSchema, OrderReadSchema
from app.service import OrderService
from app.dependencies import get_order_service
from app.rabbitmq import connect_rabbitmq, start_payments_consume


@asynccontextmanager
async def lifespan(_: FastAPI):
    from app.models import OrderItem, Order
    Base.metadata.create_all(bind=engine)

    connection = await connect_rabbitmq()
    await start_payments_consume(connection)

    try:
        yield
    finally:
        await connection.close()


app = FastAPI(lifespan=lifespan)


@app.get("/orders/{order_id}", response_model=OrderReadSchema)
def get_order(
    order_id,
    order_service: OrderService = Depends(get_order_service)
):
    return order_service.get(order_id)


@app.get("/orders", response_model=list[OrderReadSchema])
def get_order(
    order_service: OrderService = Depends(get_order_service)
):
    return order_service.get_all()


@app.post("/orders", response_model=OrderReadSchema)
def create_order(
    payload: OrderCreateSchema,
    order_service: OrderService = Depends(get_order_service)
):
    return order_service.create(payload)
