import azure.functions as func
from azure.cosmos import CosmosClient
import requests
from bs4 import BeautifulSoup
import logging
import json

def main(timer: func.TimerRequest, outputDocument: func.Out[func.Document]) -> None:
    logging.info('Starting price scraper...')

    # Cosmos DB connection
    COSMOS_DB_ENDPOINT = "YOUR_COSMOS_DB_ENDPOINT"
    COSMOS_DB_KEY = "YOUR_COSMOS_DB_KEY"
    client = CosmosClient(COSMOS_DB_ENDPOINT, COSMOS_DB_KEY)
    database = client.get_database_client("PriceComparisonDB")
    container = database.get_container_client("Products")

    # Fetch company and competitor data
    companies = container.read_all_items()
    for company in companies:
        company_name = company['company_name']
        competitors = company['competitors']
        products = company['products']

        for product in products:
            product_name = product['name']
            scraped_prices = {}
            for competitor_url in competitors:
                try:
                    # Simple scraping logic (customize per website structure)
                    response = requests.get(competitor_url, timeout=10)
                    soup = BeautifulSoup(response.content, 'html.parser')
                    # Example: Find price by class or ID (replace with actual selector)
                    price_element = soup.find('span', class_='price')
                    price = float(price_element.text.replace('$', '').strip()) if price_element else None
                    if price:
                        scraped_prices[competitor_url] = price
                except Exception as e:
                    logging.error(f"Error scraping {competitor_url}: {str(e)}")

            # Store scraped prices in Cosmos DB
            if scraped_prices:
                outputDocument.set(func.Document.from_dict({
                    'id': f"{company_name}_{product_name}",
                    'company_name': company_name,
                    'product_name': product_name,
                    'competitor_prices': scraped_prices
                }))

    logging.info('Scraping complete.')