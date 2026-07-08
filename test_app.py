import unittest
from app import app, db, Product


class TestStoreAPI(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        self.client = app.test_client()
        with app.app_context():
            db.create_all()
            db.session.add(Product(name="Test Keyboard", category="Electronics",
                                    price=3000.0, stock_quantity=10))
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_get_products(self):
        response = self.client.get('/api/products')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], "Test Keyboard")

    def test_get_product_not_found(self):
        response = self.client.get('/api/products/999')
        self.assertEqual(response.status_code, 404)

    def test_add_product_integration(self):
        payload = {"name": "Desk Fan", "category": "Home", "price": 4500, "stock_quantity": 5}
        post_response = self.client.post('/api/products', json=payload)
        self.assertEqual(post_response.status_code, 201)
        get_response = self.client.get('/api/products')
        names = [p['name'] for p in get_response.get_json()]
        self.assertIn("Desk Fan", names)

    def test_add_product_missing_fields(self):
        response = self.client.post('/api/products', json={"category": "Home"})
        self.assertEqual(response.status_code, 400)

    def test_update_product(self):
        get_response = self.client.get('/api/products')
        product_id = get_response.get_json()[0]['id']
        response = self.client.put(f'/api/products/{product_id}',
                                    json={"stock_quantity": 25, "price": 3200.0})
        self.assertEqual(response.status_code, 200)
        updated = response.get_json()
        self.assertEqual(updated['stock_quantity'], 25)
        self.assertEqual(updated['price'], 3200.0)

    def test_delete_product(self):
        get_response = self.client.get('/api/products')
        product_id = get_response.get_json()[0]['id']
        response = self.client.delete(f'/api/products/{product_id}')
        self.assertEqual(response.status_code, 200)
        follow_up = self.client.get(f'/api/products/{product_id}')
        self.assertEqual(follow_up.status_code, 404)

    def test_search_no_matches(self):
        response = self.client.get('/api/products?q=nonexistentitem')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [])


if __name__ == '__main__':
    unittest.main()
