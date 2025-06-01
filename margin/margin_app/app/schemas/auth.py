"""
This module contains Pydantic schemas for auth.
"""

from pydantic import BaseModel


class Token(BaseModel):
    """
    Auth jwt model
    """

    access_token: str
    token_type: str


class SignupConfirmation(BaseModel):
    """
    Signup confirmation request model
    """
    
    token: str
    password: str
    name: str
