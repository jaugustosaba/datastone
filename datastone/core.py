import typing


__doc__ = """
Conversion routines
"""

class Conversor:
    "I'm a conversor between currencies"

    def __init__(self,
                 reference: str, 
                 currencies: typing.Dict[str, float]) -> None:
        """
        Initializes the conversor using a reference currency (usually USD) and a dictionary relating
        every currency to its value expressed in the reference currency. The reference currency must be
        in the dictionary and its value must be 1.
        """
        if reference not in currencies:
            raise Exception(f'reference currency {reference} must be in currencies array')
        if currencies[reference] != 1.0:
            raise Exception(f'reference currency {reference} must have value 1.0')
        self.__currencies = currencies
        self.__reference = reference

    @property
    def currencies(self) -> typing.List[str]:
        "List of known currencies"
        return list(self.__currencies.keys())

    @property
    def reference(self):
        "Currency used as reference in convertions"
        return self.__reference

    def convert(self,
                currency_from: str,
                currency_to: str,
                amount: float) -> float:
        """
        Converts a 'amont' in currency 'currency_from' to currency 'currency_to'. 
        Raises an error if any of the currencies ('currency_from' or 'currency_to') are unknown.
        """
        try:
            return self.__currencies[currency_from] * amount * (1.0 / self.__currencies[currency_to])
        except KeyError as e:
            raise Exception(f'no convertion available from {currency_from} to {currency_to}')


