import asyncio
import typing
import logging
import multidict
from aiohttp import web
from . import currency
from .core import Conversor


__doc__ = """
web handling code
"""


class APIContext:
    ""
    def __init__(self, conversor: Conversor) -> None:
        self.conversor = conversor

    async def handle_currencies(self, request: web.Request) -> web.Response:
        return web.json_response(
            status=200,
            data=self.conversor.currencies,
        )

    def handle_conversion_params(self, request: web.Request) -> typing.Tuple[str, str, float]:
        params: multidict.MultiDictProxy[str] = request.query
        from0 = params.getone('from', None)
        to = params.getone('to', None)
        if from0 is None or len(from0) == 0 or to is None or len(to) == 0:
            raise Exception('missing "from" or "to" parameters')
        amount_s = params.getone('amount', None)
        if amount_s is None:
            raise Exception('missing "amount" parameter')
        amount = float(amount_s)
        return from0, to, amount


    async def handle_conversion(self, request: web.Request) -> web.Response:
        try:
            from0, to, amount = self.handle_conversion_params(request)
            logging.info(f'handling conversion: {from0}=>{to}: {amount}')
            value = self.conversor.convert(from0, to, amount)
            status = 200
            body = {
                'status': 'ok',
                'from': {
                    'currency': from0,
                    'value': amount,
                },
                'to': {
                    'currency': to,
                    'value': value,
                }
            }
        except Exception as e:
            status = 400
            body = {'status': 'error',
                    'reason': e.args[0]}
            
        return web.json_response(
            status=status,
            data=body,
        )


class ConversorMaker:
    "context for helping making a conversor fetching data from external api"
    def __init__(self,
                 reference: str, 
                 api_source: currency.APISource,
                 ConversorType: typing.Type[Conversor]) -> None:
        self.reference = reference
        self.api_source = api_source
        self.ConversorType = Conversor
        self.cache : typing.Dict[str, float] = {}
    

    async def _load_cache_entry(self, currency: str) -> None:
        "task for filling a cache entry"
        quote = await self.api_source.fetch_quote(currency, self.reference)
        if quote is None:
            return
        self.cache[currency] = quote
        logging.info(f'{currency} -> {quote}')
    

    async def make(self) -> Conversor:
        "instantiates the given conversor class with data from external service "
        currencies : typing.Dict[str, str] = await self.api_source.fetch_currencies()
        if self.reference not in currencies:
            raise Exception(f'unknown currency used as reference: {self.reference}')
        self.cache = {}
        logging.info(f'fetching last currency quotes')
        awaitables = [asyncio.create_task(self._load_cache_entry(currency)) for currency in currencies.keys()]
        await asyncio.gather(*awaitables)
        logging.info(f'currency quotes loaded')
        self.cache[self.reference] = 1.0
        return self.ConversorType(self.reference, self.cache)


def start_server(app_name: str,
                 reference: str,
                 api_source: currency.APISource,
                 ConversorType: typing.Type[Conversor],
                 port: int,
                 reuse_address: bool) -> None:
    "starts the api server using the reference, api source and conversor type given"
    base_url = ''
    if len(app_name) > 0 and not app_name.isspace():
        base_url = '/' + app_name.strip()
    loop = asyncio.get_event_loop()
    conversor_maker = ConversorMaker(reference, api_source, ConversorType)
    conversor = loop.run_until_complete(conversor_maker.make())
    logging.info('starting api handlers')
    api_context = APIContext(conversor)
    app = web.Application()
    app.add_routes([web.get(f'{base_url}/currencies', api_context.handle_currencies),
                    web.get(f'{base_url}/convert', api_context.handle_conversion)])
    web.run_app(app, port=port, reuse_address=reuse_address)


