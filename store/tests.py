import os.path
from django.conf import settings
from rest_framework.test import APITestCase

from .models import Product

class ProductCreateTestCase(APITestCase):
    def test_create_product(self):
        initial_product_count = Product.objects.count()
        payload = {
            'name' : 'Product Name',
            'description' : 'Product Description',
            'price' : 9.99,
        }
        response = self.client.post('/api/v1/products/create/', data=payload, format='json')

        self.assertEqual(
            Product.objects.count(),
            initial_product_count + 1,
        )

        for attr, expected_value in payload.items():
            self.assertEqual(
                response.data[attr],
                expected_value,
            )

        self.assertEqual(response.data['is_on_sale'], False)
        self.assertEqual(
            response.data['current_price'],
            float(payload['price']),
        )

class ProductDestroyTestCase(APITestCase):
    def test_product_delete(self):
        initial_product_count = Product.objects.count()
        product_id = Product.objects.first().id
        response = self.client.delete(f'/api/v1/products/{product_id}/')

        self.assertEqual(
            initial_product_count - 1,
            Product.objects.count(),
        )

        self.assertRaises(
            Product.DoesNotExist,
            Product.objects.get, id=product_id,
        )

class ProductListTestCase(APITestCase):
    def test_list_products(self):
        product_count = Product.objects.count()
        response = self.client.get('/api/v1/products/')

        self.assertEqual(
            product_count,
            response.data['count'],
        )
        self.assertIsNone(response.data['next'])
        self.assertIsNone(response.data['previous'])
        self.assertEqual(
            product_count,
            len(response.data['results']),
        )

class ProductUpdateTestCase(APITestCase):
    def test_update_product(self):
        product_before = Product.objects.first()
        payload = {
            'name': 'Updated Name',
            'description': 'Updated Description',
            'price': 9.95,
        }
        response = self.client.patch(f'/api/v1/products/{product_before.id}/', data=payload, format='json',)
        product_after = Product.objects.get(id=product_before.id)

        self.assertEqual(product_after.name, 'Updated Name')
        self.assertEqual(product_after.description, 'Updated Description')
        self.assertEqual(product_after.price, 9.95)

    def test_upload_product_photo(self):
        product = Product.objects.first()
        original_photo = product.photo
        photo_path = os.path.join(
            settings.MEDIA_ROOT, 'products', 'vitamin-iron.jpg',
        )

        with open(photo_path, 'rb') as photo_data:
            response = self.client.patch(
                f'/api/v1/products/{product.id}/',
                data = {
                    'photo' : photo_data,
                },
                format = 'multipart',
            )

        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.data['photo'], original_photo)

        try:
            updated_product = Product.objects.get(id=product.id)
            expected_path = os.path.join(
                settings.MEDIA_ROOT, 'products', 'vitamin-iron',
            )

            self.assertTrue(
                updated_product.photo.path.startswith(expected_path)
            )

        finally:
            os.remove(updated_product.photo.path)