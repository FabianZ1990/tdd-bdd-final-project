# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal


from service.models import Product, Category, db, DataValidationError
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    def test_update_product(self):
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        product.name = "Testproduct"
        product.update()
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)

    def test_update_empty_id(self):
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        product.name = "Testproduct"
        product.id = None
        with self.assertRaises(DataValidationError):
            product.update()

    def test_delete_product(self):
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        new_product.delete()
        products = Product.all()
        self.assertEqual(len(products), 0)

    def test_delete_product_with_multiple(self):
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        product2 = ProductFactory()
        product2.id = None
        product2.create()
        self.assertIsNotNone(product.id)
        self.assertIsNotNone(product2.id)
        products = Product.all()
        self.assertEqual(len(products), 2)
        new_product = products[0]
        new_product2 = products[1]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product2.name, product2.name)
        new_product.delete()
        products = Product.all()
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].name, new_product2.name)

    def test_serialize_to_dict(self):
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        new_product = products[0]
        dict = new_product.serialize()
        self.assertEqual(dict["id"], new_product.id)
        self.assertEqual(dict["name"], new_product.name)
        self.assertEqual(dict["description"], new_product.description)
        self.assertEqual(dict["price"], str(new_product.price))
        self.assertEqual(dict["available"], new_product.available)
        self.assertEqual(dict["category"], new_product.category.name)

    def test_deserialze(self):

        productDict = {
            "id": None,
            "name": "Red Hat",
            "description": "A red hat",
            "price": str(7.50),
            "available": True,
            "category": str("CLOTHS")
        }
        product = Product()
        product.deserialize(productDict)
        product.create()
        products = Product.all()
        self.assertEqual(products[0].name, "Red Hat")
        self.assertEqual(products[0].category.name, productDict["category"])

    def test_deserialize_available_noBool(self):

        productDict = {
            "id": None,
            "name": "Red Hat",
            "description": "A red hat",
            "price": str(7.50),
            "available": 1,
            "category": str("CLOTHS")
        }
        product = Product()
        with self.assertRaises(DataValidationError):
            product.deserialize(productDict)

    def test_deserialize_wrong_attribute(self):

        productDict = {
            "id": None,
            "name": "Red Hat",
            "description": "A red hat",
            "price": str(7.50),
            "available": True,
            "category": str("SHIT")
        }
        product = Product()
        with self.assertRaises(DataValidationError):
            product.deserialize(productDict)

    # def test_deserialize_typeerror(self):
    #     productDict =  {
    #         "id": None,
    #         "name": "Red Hat",
    #         "description": "A red hat",
    #         "available": True,
    #         "category": str("CLOTHS")
    #     }
    #     product = Product()
    #     with self.assertRaises(DataValidationError):
    #         product.deserialize(productDict)

    def test_get_all(self):
        products = Product.all()
        self.assertEqual(products, [])
        for x in range(5):
            product = ProductFactory()
            product.id = None
            product.create()
        products = Product.all()
        self.assertEqual(len(products), 5)

    def test_find_by_name(self):
        products = Product.all()
        self.assertEqual(products, [])
        product = Product(id=None, name="Fedora", description="A red hat", price=12.50, available=True,
                          category=Category.CLOTHS)
        product2 = Product(id=None, name="Bluedora", description="A blue hat", price=6.00, available=False,
                           category=Category.CLOTHS)
        product.create()
        product2.create()
        self.assertEqual(len(Product.all()), 2)
        find_product = Product.find_by_name("Fedora")
        self.assertEqual(find_product[0].description, product.description)
        self.assertEqual(find_product[0].price, product.price)

    def test_find_by_price(self):
        products = Product.all()
        self.assertEqual(products, [])
        product = Product(id=None, name="Fedora", description="A red hat", price=12.50, available=False,
                          category=Category.CLOTHS)
        product2 = Product(id=None, name="Bluedora", description="A blue hat", price=6.00, available=True,
                           category=Category.CLOTHS)
        product3 = Product(id=None, name="Greendora", description="A green hat", price=6.00, available=True,
                           category=Category.CLOTHS)
        product.create()
        product2.create()
        product3.create()
        self.assertEqual(len(Product.all()), 3)
        find_product = list(Product.find_by_price("6.00"))
        self.assertEqual(len(find_product), 2)
        self.assertEqual(find_product[0].price, 6.00)
        self.assertEqual(find_product[0].price, find_product[1].price)

    def test_find_by_availability(self):
        products = Product.all()
        self.assertEqual(products, [])
        product = Product(id=None, name="Fedora", description="A red hat", price=12.50, available=False,
                          category=Category.CLOTHS)
        product2 = Product(id=None, name="Bluedora", description="A blue hat", price=6.00, available=True,
                           category=Category.CLOTHS)
        product3 = Product(id=None, name="Greendora", description="A green hat", price=6.00, available=True,
                           category=Category.CLOTHS)
        product.create()
        product2.create()
        product3.create()
        self.assertEqual(len(Product.all()), 3)
        find_product = list(Product.find_by_availability(True))
        self.assertEqual(len(find_product), 2)
        self.assertEqual(find_product[0].available, True)
        self.assertEqual(find_product[0].available, find_product[1].available)

    def test_find_by_category(self):
        products = Product.all()
        self.assertEqual(products, [])
        product = Product(id=None, name="Fedora", description="A red hat", price=12.50, available=False,
                          category=Category.CLOTHS)
        product2 = Product(id=None, name="Bluedora", description="A blue hat", price=6.00, available=True,
                           category=Category.TOOLS)
        product3 = Product(id=None, name="Greendora", description="A green hat", price=6.00, available=True,
                           category=Category.CLOTHS)
        product.create()
        product2.create()
        product3.create()
        self.assertEqual(len(Product.all()), 3)
        find_product = list(Product.find_by_category(Category.CLOTHS))
        self.assertEqual(len(find_product), 2)
        self.assertEqual(find_product[0].category, Category.CLOTHS)
        self.assertEqual(find_product[0].category, find_product[1].category)

    def test_find_by_id(self):
        products = Product.all()
        self.assertEqual(products, [])
        product = Product(id=None, name="Fedora", description="A red hat", price=12.50, available=False,
                          category=Category.CLOTHS)
        product2 = Product(id=None, name="Bluedora", description="A blue hat", price=6.00, available=True,
                           category=Category.CLOTHS)
        product.create()
        product2.create()
        self.assertEqual(len(Product.all()), 2)
        all_products = Product.all()
        id_to_find = all_products[0].id
        find_product = Product.find(id_to_find)
        self.assertEqual(find_product.name, all_products[0].name)
