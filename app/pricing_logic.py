from azure.cosmos import CosmosClient
import pandas as pd


def compare_prices(company_name, competitors, products):
    # Cosmos DB connection
    COSMOS_DB_ENDPOINT = "YOUR_COSMOS_DB_ENDPOINT"
    COSMOS_DB_KEY = "YOUR_COSMOS_DB_KEY"
    client = CosmosClient(COSMOS_DB_ENDPOINT, COSMOS_DB_KEY)
    database = client.get_database_client("PriceComparisonDB")
    container = database.get_container_client("CompetitorPrices")

    results = {}
    for product in products:
        product_name = product['name']
        your_price = product['price']

        # Fetch scraped prices
        try:
            item = container.read_item(item=f"{company_name}_{product_name}", partition_key=company_name)
            competitor_prices = item['competitor_prices']
        except:
            competitor_prices = {}

        # Pricing strategy logic
        if competitor_prices:
            df = pd.DataFrame(list(competitor_prices.items()), columns=['Competitor', 'Price'])
            avg_price = df['Price'].mean()
            min_price = df['Price'].min()

            # Strategy:
            # - If your price > avg + 10%, recommend lowering to avg
            # - If your price < min, maintain or slightly increase
            # - If avg - 10% < your price < avg + 10%, maintain
            if your_price > avg_price * 1.1:
                recommended_price = round(avg_price, 2)
            elif your_price < min_price:
                recommended_price = round(min(your_price * 1.05, avg_price), 2)
            else:
                recommended_price = your_price
        else:
            recommended_price = your_price  # No competitor data, maintain price

        results[product_name] = {
            'your_price': your_price,
            'competitor_prices': competitor_prices,
            'recommended_price': recommended_price
        }

    return results