import logging
from decimal import Decimal
from typing import Dict


from margin_app.app.utils.token_params import TokenParams 
from margin_app.app.core.config import AVNU_PRICE_URL 


from ..api_client import BaseAPIClient

logger = logging.getLogger(__name__)


class AdminMixin:

    @classmethod
    async def get_current_prices(cls) -> Dict[str, Decimal]:
      
        prices = {}
        api_client = BaseAPIClient(base_url=AVNU_PRICE_URL)

        
        response_data = await api_client.get("")

        if not response_data:
            logger.warning("Received no data from AVNU price API.")
            return prices

        if not isinstance(response_data, list):
            logger.error(f"Unexpected data format from AVNU API. Expected list, got {type(response_data)}.")
            return prices

        for token_data in response_data:
            address = token_data.get("address")
            current_price = token_data.get("currentPrice")

            if not (address and current_price is not None):
                logger.debug(f"Skipping token data due to missing address or price: {token_data}")
                continue
            try:                
                address_with_leading_zero = TokenParams.add_underlying_address(address)
                symbol = TokenParams.get_token_symbol(address_with_leading_zero)

                if symbol:                 
                    prices[symbol] = Decimal(str(current_price))
            except (AttributeError, TypeError, ValueError) as e:
                logger.debug(f"Error parsing price for address {address}: {str(e)}")

        return prices
