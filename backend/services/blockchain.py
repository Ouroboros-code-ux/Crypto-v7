import requests
import logging
from ..config import ETHERSCAN_API_KEY

logger = logging.getLogger(__name__)

class ChainProvider:
    BASE_URL = "https://api.etherscan.io/v2/api"
    TIMEOUT = 10

    @staticmethod
    def fetch_history(address: str, chain: str = "ETH"):
        logger.debug(f"Fetching data for {address} on {chain}...")
        
        params = {
            "module": "account",
            "action": "txlist",
            "address": address,
            "startblock": 0,
            "endblock": 99999999,
            "page": 1,
            "offset": 1000,
            "sort": "desc",
            "apikey": ETHERSCAN_API_KEY
        }
        
        if chain == "POLYGON":
            params["chainid"] = 137
        else:
             params["chainid"] = 1
        
        try:
            response = requests.get(ChainProvider.BASE_URL, params=params, timeout=ChainProvider.TIMEOUT)
            data = response.json()
            
            if data.get("status") != "1" and data.get("message") != "No transactions found":
                logger.error(f"{chain} API Error: {data.get('result')}")
                return []
                
            return data.get("result", [])
        except requests.Timeout:
            logger.error(f"Timeout fetching {chain} history for {address}")
            return []
        except Exception as e:
            logger.exception(f"Error fetching {chain} history: {e}")
            return []

fetch_chain_history = ChainProvider.fetch_history