import asyncio
import typing
import logging
import multidict
from aiohttp import web
from . import currency
from .core import Conversor


__doc__ = """web handling code"""


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
    

def check_conversor_availability(f: typing.Callable[..., typing.Awaitable[web.Response]]) -> typing.Callable[..., typing.Awaitable[web.Response]]:
    "decorator for handling requests when the coversor is not available yet"
    async def wrap(self, request: web.Request, *args, **kargs) -> web.Response:
        if self.conversor is None:
            return web.json_response(
                status=503,
                data={
                    'status': 'loading',
                    'reason': 'currency data not available yet',
                }
            )
        return await f(self, request, *args, **kargs)
    return wrap


class APIContext:
    ""
    def __init__(self, conversor_maker: ConversorMaker) -> None:
        self.conversor_maker = conversor_maker
        self.conversor: typing.Optional[Conversor] = None

    @check_conversor_availability
    async def handle_currencies(self, request: web.Request) -> web.Response:
        assert self.conversor is not None
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

    @check_conversor_availability
    async def handle_conversion(self, request: web.Request) -> web.Response:
        assert self.conversor is not None
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
    

    async def reload_conversor(self, delay_secs: float) -> None:
        "continously reload conversor data with new currency data after a delay"
        while True:
            logging.info('reloading currency data for building a new conversor')
            try:
                self.conversor = await self.conversor_maker.make()
            except Exception as e:
                logging.error('cannot make currency conversor')
            await asyncio.sleep(delay_secs)



def start_server(app_name: str,
                 reference: str,
                 api_source: currency.APISource,
                 ConversorType: typing.Type[Conversor],
                 port: int,
                 reuse_address: bool,
                 reload_timeout: float) -> None:
    "starts the api server using the reference, api source and conversor type given"
    base_url = ''
    if len(app_name) > 0 and not app_name.isspace():
        base_url = '/' + app_name.strip()
    
    logging.info('starting api handlers')
    conversor_maker = ConversorMaker(reference, api_source, ConversorType)
    api_context = APIContext(conversor_maker)
    reload_task: typing.Optional[asyncio.Task] = None

    async def startup(app: web.Application):
        "app startup hook"
        logging.info('app startup')
        nonlocal reload_task
        # starts the conversor reload 
        # task that will update currency data every reload_timeout secs.
        loop = asyncio.get_event_loop()
        reload_task = loop.create_task(api_context.reload_conversor(reload_timeout))

    async def shutdown(app: web.Application):
        "app shutdown hook"
        logging.info('app shutdown')
        assert reload_task is not None
        # kills the conversor reload task
        reload_task.cancel()

    app = web.Application()
    app.add_routes([web.get(f'{base_url}/currencies', api_context.handle_currencies),
                    web.get(f'{base_url}/convert', api_context.handle_conversion)])
    app.on_startup.append(startup)
    app.on_shutdown.append(shutdown)
    web.run_app(app, port=port, reuse_address=reuse_address, )


