import azure.functions as func
from azure.cosmos import CosmosClient
import json
from config.azure_config import COSMOS_DB_ENDPOINT, COSMOS_DB_KEY


def main(req: func.HttpRequest) -> func.HttpResponse:
    client = CosmosClient(COSMOS_DB_ENDPOINT, COSMOS_DB_KEY)
    database = client.get_database_client("PriceComparisonDB")
    container = database.get_container_client("CompetitorPrices")

    try:
        company_name = req.params.get('company_name')
        product_name = req.params.get('product_name')

        item = container.read_item(item=f"{company_name}_{product_name}", partition_key=company_name)
        competitor_prices = item['competitor_prices']

        # Simplified pricing logic for API
        df = pd.DataFrame(list(competitor_prices.items()), columns=['Competitor', 'Price'])
        recommended_price = round(df['Price'].mean(), 2)

        return func.HttpResponse(json.dumps({
            'product_name': product_name,
            'recommended_price': recommended_price,
            'competitor_prices': competitor_prices
        }), status_code=200)
    except Exception as e:
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)