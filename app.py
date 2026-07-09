from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///store.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock_quantity = db.Column(db.Integer, nullable=False, default=0)

    def to_dict(self):
        return {
            "id": self.id, "name": self.name, "category": self.category,
            "price": self.price, "stock_quantity": self.stock_quantity,
        }


def seed_data():
    if Product.query.count() == 0:
        sample_products = [
            Product(name="Wireless Mouse", category="Electronics", price=1500.00, stock_quantity=40),
            Product(name="Bluetooth Speaker", category="Electronics", price=6500.00, stock_quantity=15),
            Product(name="Notebook Set", category="Stationery", price=350.00, stock_quantity=100),
            Product(name="Ceramic Mug", category="Kitchenware", price=800.00, stock_quantity=60),
            Product(name="Desk Lamp", category="Home", price=2200.00, stock_quantity=25),
        ]
        db.session.bulk_save_objects(sample_products)
        db.session.commit()


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/api/products', methods=['GET'])
def get_products():
    query = request.args.get('q', '').strip().lower()
    products = Product.query.all()
    if query:
        products = [p for p in products if query in p.name.lower() or query in p.category.lower()]
    return jsonify([p.to_dict() for p in products]), 200


@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = db.session.get(Product, product_id)
    if product is None:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(product.to_dict()), 200


@app.route('/api/products', methods=['POST'])
def add_product():
    data = request.get_json(silent=True)
    if not data or 'name' not in data or 'price' not in data:
        return jsonify({"error": "Missing required fields: name, price"}), 400
    new_product = Product(
        name=data['name'],
        category=data.get('category', 'General'),
        price=float(data['price']),
        stock_quantity=int(data.get('stock_quantity', 0)),
    )
    db.session.add(new_product)
    db.session.commit()
    return jsonify(new_product.to_dict()), 201


@app.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    product = db.session.get(Product, product_id)
    if product is None:
        return jsonify({"error": "Product not found"}), 404
    data = request.get_json(silent=True) or {}
    if 'price' in data:
        product.price = float(data['price'])
    if 'stock_quantity' in data:
        product.stock_quantity = int(data['stock_quantity'])
    if 'name' in data:
        product.name = data['name']
    if 'category' in data:
        product.category = data['category']
    db.session.commit()
    return jsonify(product.to_dict()), 200


@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    product = db.session.get(Product, product_id)
    if product is None:
        return jsonify({"error": "Product not found"}), 404
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": f"Product {product_id} deleted"}), 200


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_data()
    app.run(debug=True)