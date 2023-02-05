import asyncio
import typing
import logging
import multidict
import aiohttp
from aiohttp import web

CurDict = typing.Dict[str, str]

base: str = 'USD'
cache: typing.Dict[str, float] = {
    base : 1.0,
}

async def fetch_currencies() -> CurDict:
    async with aiohttp.ClientSession() as session:
        async with session.get('https://economia.awesomeapi.com.br/json/available/uniq') as resp:
            return await resp.json()


async def fetch_quote(currency: str) -> typing.Union[float, None]:
    async with aiohttp.ClientSession() as session:
        async with session.get(f'http://economia.awesomeapi.com.br/json/last/{currency}-{base}') as resp:
            payload = await resp.json()
            if resp.status != 200:
                return None
            return float(payload[f'{currency}{base}']['bid'])


async def handle_currencies(request: web.Request) -> web.Response:
    return web.json_response(
        status=200,
        data=list(cache.keys()),
    )


def convert(currency_from: str,
            currency_to: str,
            amount: float) -> float:
    try:
        return cache[currency_from] * amount * (1.0 / cache[currency_to])
    except KeyError as e:
        raise Exception(f'no convertion available from {currency_from} to {currency_to}')


def handle_conversion_params(request: web.Request) -> typing.Tuple[str, str, float]:
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


async def handle_conversion(request: web.Request) -> web.Response:
    try:
        from0, to, amount = handle_conversion_params(request)
        logging.info(f'handling conversion: {from0}=>{to}: {amount}')
        value = convert(from0, to, amount)
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



async def load_cache_entry(currency: str) -> None:
    quote = await fetch_quote(currency)
    if quote is None:
        return
    cache[currency] = quote
    print(f'{currency}: {quote}')
  

async def start() -> None:
    currencies : CurDict = await fetch_currencies()
    await asyncio.gather(*[asyncio.create_task(load_cache_entry(currency)) for currency in currencies.keys()])


def main() -> None:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start())
    app = web.Application()
    app.add_routes([web.get('/currencies', handle_currencies),
                    web.get('/convert', handle_conversion)])
    web.run_app(app)


if __name__ == '__main__':
    main()