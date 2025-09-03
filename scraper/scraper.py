import azure.functions as func
from azure.cosmos import CosmosClient
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
import requests
from bs4 import BeautifulSoup
import logging
import json
from config.azure_config import COSMOS_DB_ENDPOINT, COSMOS_DB_KEY, COGNITIVE_SERVICES_ENDPOINT, COGNITIVE_SERVICES_KEY

def main(req: func.HttpRequest, outputDocument: func.Out[func.Document]) -> func.HttpResponse:
    logging.info('Starting price scraper...')

    client = CosmosClient(COSMOS_DB_ENDPOINT, COSMOS_DB_KEY)
    database = client.get_database_client("PriceComparisonDB")
    container = database.get_container_client("Products")
    ta_client = TextAnalyticsClient(COGNITIVE_SERVICES_ENDPOINT, AzureKeyCredential(COGNITIVE_SERVICES_KEY))

    try:
        req_body = req.get_json()
        company_name = req_body.get('company_name')
        product_name = req_body.get('product_name')
        product_desc = req_body.get('product_description')
        competitors = req_body.get('competitors')

        scraped_prices = {}
        for competitor_url in competitors:
            try:
                response = requests.get(competitor_url, timeout=10)
                soup = BeautifulSoup(response.content, 'html.parser')
                # Example: Find product name and price (customize per website)
                products = soup.find_all('div', class_='product')  # Adjust selector
                for prod in products:
                    name = prod.find('h2').text if prod.find('h2') else ''
                    price = prod.find('span', class_='price')
                    price = float(price.text.replace('$', '').strip()) if price else None
                    if name and price:
                        # Match products using Text Analytics
                        result = ta_client.analyze_sentiment(documents=[product_desc, name])[0]
                        similarity = result.confidence_scores.positive  # Simplified similarity metric
                        if similarity > 0.7:  # Threshold for match
                            scraped_prices[competitor_url] = price
                            break
            except Exception as e:
                logging.error(f"Error scraping {competitor_url}: {str(e)}")

        if scraped_prices:
            outputDocument.set(func.Document.from_dict({
                'id': f"{company_name}_{product_name}",
                'company_name': company_name,
                'product_name': product_name,
                'competitor_prices': scraped_prices
            }))

        return func.HttpResponse(json.dumps({'status': 'success', 'prices': scraped_prices}), status_code=200)
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)