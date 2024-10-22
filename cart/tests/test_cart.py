from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from cart.models import Cart, CartItem
from book.models import Book

User = get_user_model()

class CartAPITestCase(APITestCase):

    def setUp(self):
    # Setup a user and authentication
        self.user = User.objects.create_user(
            email='ombhamare2002@gmail.com',
            password='Vinit@2002',
            first_name='Om',
            last_name='Bhamare'
        )
        self.client.force_authenticate(user=self.user)
        
        # Setup a book for testing with the user
        self.book = Book.objects.create(
            name='Test Book',
            author='Vinit',
            stock=10,
            price=1000,
            user=self.user  # Add the user field here
        )

        # Create a cart for the user
        self.cart = Cart.objects.create(user=self.user, total_price=0, total_quantity=0, is_ordered=False)

    def test_list_cart(self):
        """
        Test to list the user's cart
        """
        url = reverse('cart-list')  # Assuming cart-list is the correct url name
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'user' in response.data
        assert response.data['user'] == self.user.id

    def test_create_cart_item(self):
        """
        Test to add a book to the user's cart
        """
        url = reverse('cart-list')  # Assuming cart-list is the correct url name
        data = {
            'book_id': self.book.id,
            'quantity': 2
        }
        response = self.client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'data' in response.data
        assert response.data['data']['total_quantity'] == 2
        assert response.data['data']['total_price'] == 2000
    
    def test_create_cart_item_invalid_book(self):
        """
        Test adding an invalid book to the cart (non-existent book)
        """
        url = reverse('cart-list')  # Assuming cart-list is the correct url name
        data = {
            'book_id': 9999,  # Invalid book ID
            'quantity': 1
        }
        response = self.client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert 'error' in response.data
        assert response.data['error'] == "Book not found."
        
    def test_delete_cart_item(self):
        """
        Test to delete an item from the cart
        """
        cart_item = CartItem.objects.create(cart=self.cart, book=self.book, quantity=2, price=200)
        url = reverse('cart-detail', args=[cart_item.id])  # Assuming cart-detail is the correct url name
        response = self.client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        self.cart.refresh_from_db()
        assert self.cart.total_quantity == 0
        assert self.cart.total_price == 0
    
    def test_order_cart(self):
        """
        Test to order the cart
        """
        cart_item = CartItem.objects.create(cart=self.cart, book=self.book, quantity=2, price=200)
        url = reverse('carts-order-cart')  # Assuming cart-order_cart is the correct url name
        response = self.client.patch(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'message' in response.data
        assert response.data['message'] == 'Cart has been successfully ordered.'
        self.cart.refresh_from_db()
        assert self.cart.is_ordered
        self.book.refresh_from_db()
        assert self.book.stock == 8  # Stock should decrease

    def test_order_cart_empty(self):
        """
        Test trying to order an empty cart
        """
        url = reverse('cart-order_cart')  # Assuming cart-order_cart is the correct url name
        response = self.client.patch(url)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data
        assert response.data['error'] == 'Your cart is empty. Please add items before placing an order.'

    def test_delete_cart(self):
        """
        Test to delete the entire cart
        """
        cart_item = CartItem.objects.create(cart=self.cart, book=self.book, quantity=2, price=200)
        url = reverse('cart-delete_cart')  # Assuming cart-delete_cart is the correct url name
        response = self.client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Cart.objects.filter(id=self.cart.id).exists()
