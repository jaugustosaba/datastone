import aiohttp
import typing


__doc__ = """
Currency data source
"""

class APISource:
    "source for external currency data"

    def __init__(self, base_url: str = 'https://economia.awesomeapi.com.br') -> None:
        self.base_url = base_url

    async def fetch_currencies(self) -> typing.Dict[str, str]:
        "fetches currencies as a map of name => description"
        async with aiohttp.ClientSession() as session:
            async with session.get(f'{self.base_url}/json/available/uniq') as resp:
                return await resp.json()


    async def fetch_quote(self,
                          currency: str, reference: str) -> typing.Union[float, None]:
        "fetches the last quotes of a given currency"
        async with aiohttp.ClientSession() as session:
            async with session.get(f'http://economia.awesomeapi.com.br/json/last/{currency}-{reference}') as resp:
                payload = await resp.json()
                if resp.status != 200:
                    return None
                return float(payload[f'{currency}{reference}']['bid'])
