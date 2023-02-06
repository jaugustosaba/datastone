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
mypy datastone
```

required output
```
Success: no issues found in 6 source files
```

### testing

The builtin unittest facility in python is used for running tests

```shell
python3 -m unittest datastone.core_test
```

### execution

For a execution using default values:

```shell
python3 -m datastone
```

For a list of running options:

```shell
python3 -m datastone --help
```

### code structure

The code is structured using python's modules:

| module | description |
| - | - |
| datastone | parent module for grouping core, web and currency submodules |
| datastone.core | currency conversion data (pure code) |
| datastone.currency | external currency data access |
| datastone.web | api handlers |

## deploy

This section contains instructions for building, running and acessing services.

### building

The preferred way of preparing for execution is using docker for building a container:

```shell
docker build . -t datastone
```

The container *datastone* will contain all dependencies needed for execution.

### execution

You may use docker for managing the execution of previous build image. ***Do not forget to forward host port to the container port 8080*** (-p option; may vary due to container's environment vars):

```shell
docker run -it -p 8080:8080 datastone
```

Container's enviroment varibles

| environment variable | default value | description |
| - | - | - |
| DS_APP_NAME | datastone | root service path (GET /$DS_APP_NAME/...) |
| DS_AWESOME_API | https://economia.awesomeapi.com.br | endpoint for currency data source |
| DS_REFERENCE | USD | currency used as reference |
| DS_PORT | 8080 | port used by the API server |
| DS_REUSE_ADDR | false | should reuse address ? |
| DS_LOG_LEVEL | INFO | application log level |

### endpoints

The services of this project are provided as simple rest APIs. The results are coded in JSON format. The examples below assumes your server is runinning in your local machine on port 8080.

#### GET /datastone/currencies

Lists the currencies available for conversions. Eg:

```shell
curl -X GET "http://localhost:8080/datastone/currencies"
```

outputs:

```json
["USD", "EGP", "DKK", "DOGE", "KYD", "XBR", "NOK", "XRP", "XAGG", "AED", "ETH", "EUR", "FJD", "GBP", "VND", "LTC", "ZAR", "THB", "SEK", "PLN", "PHP", "ILS", "KWD", "NZD", "NIO", "IQD", "INR", "JPY", "GHS", "KRW", "IDR", "IRR", "MXN", "SAR", "HUF", "PYG", "MYR", "SGD", "PEN", "RUB", "TWD", "UAH", "HKD", "UYU", "SYP", "JOD", "TRY", "AUD", "CAD", "BRL", "CHF", "COP", "AFN", "CNY", "BYN", "BOB", "BTC", "CLP", "ARS"]
```

#### GET /datastone/convert

Converts between currencies. Eg:

```shell
curl -X GET "http://localhost:8080/datastone/convert?from=BRL&to=GBP&amount=100"
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
curl -X GET "http://localhost:8080/datastone/convert?from=BRL&to=UTC&amount=100"
```

outputs:

```json
{
    "status": "error", 
    "reason": "no convertion available from BRL to UTC"
}
```