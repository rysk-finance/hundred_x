"""
Async client for the HundredX API
"""
import httpx
import requests
from decimal import Decimal

from hundred_x.client import HundredXClient
from hundred_x.eip_712 import Order
from hundred_x.enums import OrderSide, OrderType, TimeInForce
from hundred_x.utils import from_message_to_payload, get_abi

class AsyncHundredXClient(HundredXClient):
    """
    Asynchronous client for the HundredX API.
    """

    async def create_and_send_order(
        self,
        subaccount_id: int,
        product_id: int,
        quantity: int,
        price: int,
        side: OrderSide,
        order_type: OrderType,
        time_in_force: TimeInForce,
        nonce: int = 0,
    ):
        """
        Create and send order.
        """
        ts = self._current_timestamp()
        if nonce == 0:
            nonce = ts
        message = self.generate_and_sign_message(
            Order,
            subAccountId=subaccount_id,
            productId=product_id,
            quantity=int(Decimal(str(quantity)) * Decimal(1e18)),
            price=int(Decimal(str(price)) * Decimal(1e18)),
            isBuy=side.value,
            orderType=order_type.value,
            timeInForce=time_in_force.value,
            nonce=nonce,
            expiration=(ts + 1000 * 60 * 60 * 24) * 1000,
            **self.get_shared_params(),
        )
        response = await self.send_message_to_endpoint("/v1/order", "POST", message)
        return response

    async def send_message_to_endpoint(self, endpoint: str, method: str, message: dict, authenticated: bool = True):
        """
        Send a message to an endpoint.
        """
        payload = from_message_to_payload(message)
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method,
                self.rest_url + endpoint,
                headers={} if not authenticated else self.authenticated_headers,
                json=payload,
            )
            if response.status_code != 200:
                raise Exception(f"Failed to send message: {response.text} {response.status_code} {self.rest_url} {payload}")
            return response.json()

    async def list_products(self):
        """
        List all products available on the exchange.
        """
        return super().list_products()

    async def get_product(self, symbol: str):
        """
        Get a specific product available on the exchange.
        """
        return super().get_product(symbol)

    async def get_server_time(self):
        """
        Get the server time.
        """
        return super().get_server_time()
