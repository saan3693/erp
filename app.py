from flask import Flask, render_template, request, redirect, url_for
import csv

app = Flask(__name__)
FILE_PATH = 'inventory.csv'

# --- Inventory Logic (from original inventory.py) ---

def initialize_inventory():
    try:
        with open(FILE_PATH, mode='x', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Product ID", "Product Name", "Category", "Price", "Stock", "Total Sales"])
    except FileExistsError:
        pass

def read_inventory():
    try:
        with open(FILE_PATH, mode='r') as file:
            reader = csv.DictReader(file)
            return list(reader)
    except FileNotFoundError:
        return []

def write_inventory(rows):
    with open(FILE_PATH, mode='w', newline='') as file:
        fieldnames = ["Product ID", "Product Name", "Category", "Price", "Stock", "Total Sales"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

# --- Flask Routes ---

@app.route('/', methods=['GET', 'POST'])
def index():
    initialize_inventory()
    inventory = read_inventory()

    if request.method == 'POST':
        if 'add' in request.form:
            product_id = request.form['product_id']
            product_name = request.form['product_name']
            category = request.form['category']
            price = float(request.form['price'])
            stock = int(request.form['stock'])

            if any(row['Product ID'] == product_id for row in inventory):
                return render_template('index.html', inventory=inventory, error="Product ID already exists.")

            with open(FILE_PATH, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([product_id, product_name, category, price, stock, 0])
            return redirect(url_for('index'))

        elif 'update' in request.form:
            product_id = request.form['product_id_update']
            updated_inventory = []
            for row in inventory:
                if row['Product ID'] == product_id:
                    row['Product Name'] = request.form.get('product_name_update', row['Product Name'])
                    row['Category'] = request.form.get('category_update', row['Category'])
                    row['Price'] = request.form.get('price_update', row['Price'])
                    row['Stock'] = request.form.get('stock_update', row['Stock'])
                updated_inventory.append(row)
            write_inventory(updated_inventory)
            return redirect(url_for('index'))

        elif 'sale' in request.form:
            product_id = request.form['product_id_sale']
            quantity = int(request.form['quantity'])
            updated_inventory = []
            for row in inventory:
                if row['Product ID'] == product_id:
                    if int(row['Stock']) >= quantity:
                        row['Stock'] = str(int(row['Stock']) - quantity)
                        row['Total Sales'] = str(int(row['Total Sales']) + quantity)
                    else:
                        return render_template('index.html', inventory=inventory, error="Insufficient Stock.")
                updated_inventory.append(row)
            write_inventory(updated_inventory)
            return redirect(url_for('index'))

        elif 'restock' in request.form:
            threshold = int(request.form['threshold'])
            restock_products = [row for row in inventory if int(row['Stock']) < threshold]
            return render_template('index.html', inventory=inventory, restock_products=restock_products)

    return render_template('index.html', inventory=inventory)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')