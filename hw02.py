""" Завантаження курсу валюти за певну кількість днів. Код валюти і кількість днів вказуються користувачем """

import argparse
import logging
from datetime import datetime, timedelta

import aiohttp
import asyncio


async def request(url: str):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    r = await resp.json()
                    return r
                logging.error(f"Error status: {resp.status} for {url}")
                return None
        except aiohttp.ClientConnectorError as err:
            logging.error(f"Connection error: {str(err)}")
            return None


async def get_exchange(currency_code: str, days: int):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    for single_date in (start_date + timedelta(n) for n in range(days)):
        formatted_date = single_date.strftime("%d.%m.%Y")
        result = await request(
            f"https://api.privatbank.ua/p24api/exchange_rates?json&date={formatted_date}"
        )

        if result:
            rates = result.get("exchangeRate")
            try:
                exc = next(item for item in rates if item["currency"] == currency_code)
                print(
                    f"{currency_code}: buy: {exc['purchaseRate']}, sale: {exc['saleRate']}. Date: {formatted_date}"
                )
            except StopIteration:
                print(f"No data available for {currency_code} on {formatted_date}")
        else:
            print(f"Failed to retrieve data for {formatted_date}")


def main():
    parser = argparse.ArgumentParser(
        description="Get exchange rates for a specific currency and days"
    )
    parser.add_argument("currency_code", type=str, help="Currency code (e.g., EUR)")
    parser.add_argument(
        "days", type=int, help="Number of days for which to get exchange rates"
    )

    args = parser.parse_args()

    asyncio.run(get_exchange(args.currency_code, args.days))


if __name__ == "__main__":
    main()
