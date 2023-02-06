import argparse
import sys
import os
import logging
from .web import start_server
from .core import Conversor
from .currency import APISource


__doc__ = """
command line api
"""


_loglevel = {
    'CRITICAL': logging.CRITICAL,
    'FATAL': logging.FATAL,
    'ERROR': logging.ERROR,
    'WARNING': logging.WARNING,
    'INFO': logging.INFO,
    'DEBUG': logging.DEBUG,
}


def main():
    "entry point for command line"
    parser = argparse.ArgumentParser(
        prog=f"python3 -m {__package__}",
        description='Currency conversor api service',
    )
    parser.add_argument('--app-name', dest='app_name', type=str, default=__package__)
    parser.add_argument('--awesome-api', dest='api_source', type=str, default='https://economia.awesomeapi.com.br')
    parser.add_argument('--reference', dest='reference', type=str, default='USD')
    parser.add_argument('--port', dest='port', type=int, default=8080)
    parser.add_argument('--reuse-address', dest='reuse_address', type=bool, default=False)
    parser.add_argument('--log-level', dest='loglevel', type=str, choices=list(_loglevel.keys()), default='INFO')
    parser.add_argument('--reload-timeout', dest='reload_timeout', type=int, default=5*60)
    args = parser.parse_args()
    try:
        logging.basicConfig(level=_loglevel[args.loglevel])
        start_server(
            app_name=args.app_name,
            reference=args.reference,
            api_source=APISource(args.api_source),
            ConversorType=Conversor,
            port=args.port,
            reuse_address=args.reuse_address,
            reload_timeout=args.reload_timeout,
        )
    except Exception as e:
        print(str(e), file=sys.stderr)
        os.exit(1)


if __name__ == '__main__':
    main()