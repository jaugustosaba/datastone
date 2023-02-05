# datastone

Basic currency conversion service utility.

## dependencies

* python >= 3.9
* aiohttp >= 3.8.3
* docker >= 20.10.5

# external services

We consume the APIs from [awesomeapi](https://docs.awesomeapi.com.br/api-de-moedas) for currency data, particularly the below endpoints.  

| endpoint | usage |
| - | - |
| https://economia.awesomeapi.com.br/json/available/uniq | provides a list o currencies |
| http://economia.awesomeapi.com.br/json/last/ | provides the last bid value for a currency |

## development 

This software is written in *python* using the library *aiohttp*. The library *mypy* is required only when dealing with code.

### extra dependencies

The following dependencies are required for development

* mypy >= 0.991

### setup

For development use virtualenv for not messing your system's packages:

```shell
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/dev.txt
```

### typechecking

Use *mypy* to check types before execution. ***No type errors are expected***.

```shell
mypy main.py
```

## Usage

This section contains instructions for building, running and acessing services.

## building

The preferred way of preparing for execution is using docker for building a container:

```shell
docker build . -t datastone
```

The container *datastone* will contain all dependencies needed for execution.

## running

You may use docker for managing the execution of previous build image. ***Do not forget to forward host port to the container port 8080*** (-p option):

```shell
docker run -it -p 8080:8080 datastone
```

## services

The services of this project are provided as simple rest APIs. The results are coded in JSON format. The examples below assumes your server is runinning in your local machine on port 8080.

### GET /currencies

Lists the currencies available for conversions. Eg:

```shell
curl -X GET "http://localhost:8080/currencies"
```

outputs:

```json
["USD", "EGP", "DKK", "DOGE", "KYD", "XBR", "NOK", "XRP", "XAGG", "AED", "ETH", "EUR", "FJD", "GBP", "VND", "LTC", "ZAR", "THB", "SEK", "PLN", "PHP", "ILS", "KWD", "NZD", "NIO", "IQD", "INR", "JPY", "GHS", "KRW", "IDR", "IRR", "MXN", "SAR", "HUF", "PYG", "MYR", "SGD", "PEN", "RUB", "TWD", "UAH", "HKD", "UYU", "SYP", "JOD", "TRY", "AUD", "CAD", "BRL", "CHF", "COP", "AFN", "CNY", "BYN", "BOB", "BTC", "CLP", "ARS"]
```

### GET /convert

Converts between currencies. Eg:

```shell
curl -X GET "http://localhost:8080/convert?from=BRL&to=GBP&amount=100"
```

outputs:

```json
{
    "status": "ok",
    "from": {
        "currency": "BRL",
        "value": 100.0
    },
    "to": {
        "currency": "GBP",
        "value": 16.13064073797058
    }
}
```

The parameters used in the query are described below:

| parameter | type | description |
| - | - | - |
| from | string | the symbol of the currency of the current value |
| to | string | the symbol of the currency you want to convert into |
| amount | real | the amount you want to know the value in the new currency |

If an error occurs, the response field "status" will contain a "error" string and a "reason" field with a string providing futher details. Eg:

```shell
curl -X GET "http://localhost:8080/convert?from=BRL&to=UTC&amount=100"
```

outputs:

```json
{
    "status": "error", 
    "reason": "no convertion available from BRL to UTC"
}
```