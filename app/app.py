from flask import Flask, request, render_template
from azure.cosmos import CosmosClient
import pandas as pd
import json
from pricing_logic import compare_prices  # Import pricing logic (defined later)

app = Flask(__name__)

# Azure Cosmos DB configuration
COSMOS_DB_ENDPOINT = "YOUR_COSMOS_DB_ENDPOINT"
COSMOS_DB_KEY = "YOUR_COSMOS_DB_KEY"
COSMOS_DB_DATABASE = "PriceComparisonDB"
COSMOS_DB_CONTAINER = "Products"

client = CosmosClient(COSMOS_DB_ENDPOINT, COSMOS_DB_KEY)
database = client.get_database_client(COSMOS_DB_DATABASE)
container = database.get_container_client(COSMOS_DB_CONTAINER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    # Get form data
    company_name = request.form['company_name']
    competitors = [request.form[f'competitor_{i}'] for i in range(1, 11) if request.form.get(f'competitor_{i}')]
    products = []
    for i in range(1, 21):
        product_name = request.form.get(f'product_name_{i}')
        product_price = request.form.get(f'product_price_{i}')
        if product_name and product_price:
            products.append({'name': product_name, 'price': float(product_price)})

    # Store data in Cosmos DB
    item = {
        'id': company_name.replace(" ", "_"),
        'company_name': company_name,
        'competitors': competitors,
        'products': products
    }
    container.upsert_item(item)

    # Trigger price comparison (assuming scraped data is available)
    comparison_results = compare_prices(company_name, competitors, products)

    return render_template('results.html', results=comparison_results)

if __name__ == '__main__':
    app.run(debug=True)