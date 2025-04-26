from pydantic import BaseModel


class StatisticResponse(BaseModel):
    """
    Response model for getting total amount of: 
    users, opened positions, liquidated positions, opened orders
    """
   
    users: int
    opened_positions: int
    liquidated_positions: int
    opened_orders: int