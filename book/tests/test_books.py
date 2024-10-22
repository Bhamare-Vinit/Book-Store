import pytest
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from book.models import Book
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestBookViewSet(APITestCase):

    def setUp(self):
        # Create a regular user
        self.user = User.objects.create_user(
            first_name="Regular",
            last_name="User",
            email="regular@example.com",
            password="password123",
            is_superuser=False
        )

        # Create a superuser
        self.superuser = User.objects.create_user(
            first_name="Super",
            last_name="User",
            email="super@example.com",
            password="password123",
            is_superuser=True
        )

        # Login URLs
        self.login_url = reverse('login')
        self.book_list_url = reverse('book-list')
    
    def authenticate(self, is_superuser=False):
        """Helper method for user authentication"""
        user = self.superuser if is_superuser else self.user
        self.client.force_authenticate(user=user)

    def test_list_books_authenticated(self):
        """Test: List books when the user is authenticated"""
        self.authenticate()  # Authenticated user
        response = self.client.get(self.book_list_url)
        assert response.status_code == status.HTTP_200_OK
        assert "Notes retrieved successfully." in response.data['message']

    def test_list_books_unauthenticated(self):
        """Test: List books should fail if not authenticated"""
        response = self.client.get(self.book_list_url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_book_as_superuser(self):
        """Test: Create a book as a superuser"""
        self.authenticate(is_superuser=True)
        data = {
                "name": "book7",
                "author":"Vinit",
                "description": "me__",
                "price":300,
                "stock":55
        }
        response = self.client.post(self.book_list_url, data=data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['message'] == 'Note created successfully.'

    def test_create_book_as_regular_user(self):
        """Test: Regular user should not be allowed to create books"""
        self.authenticate()
        data = {
                "name": "book7",
                "author":"Vinit",
                "description": "me__",
                "price":300,
                "stock":55
        }
        response = self.client.post(self.book_list_url, data=data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Only superusers can create books." in response.data['detail']

    def test_retrieve_book(self):
        """Test: Retrieve a single book"""
        self.authenticate()
        # First create a book
        book = Book.objects.create(name="Book10", author="Author1123",price=100,stock=10, user=self.superuser)
        url = reverse('book-detail', kwargs={'pk': book.id})
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['message'] == 'Book retrieved successfully.'

    def test_update_book_as_superuser(self):
        """Test: Update a book as superuser"""
        self.authenticate(is_superuser=True)
        book = Book.objects.create(name="Book10", author="Author1123",price=100,stock=10, user=self.superuser)
        url = reverse('book-detail', kwargs={'pk': book.id})
        data = {
            "name": "Update_Book",
            "author": "Updated_Author",
            "price": 200,
            "stock": 20
        }
        response = self.client.put(url, data=data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['message'] == 'Note updated successfully.'

    def test_partial_update_book(self):
        """Test: Partial update of a book"""
        self.authenticate(is_superuser=True)
        book = Book.objects.create(name="Book10", author="Author1123",price=100,stock=10, user=self.superuser)
        url = reverse('book-detail', kwargs={'pk': book.id})
        data = {
            "name": "Updated Title"
        }
        response = self.client.patch(url, data=data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['message'] == 'Note partially updated successfully.'

    def test_delete_book_as_superuser(self):
        """Test: Delete a book as superuser"""
        self.authenticate(is_superuser=True)
        book = Book.objects.create(name="Book10", author="Author1123",price=100,stock=10, user=self.superuser)
        url = reverse('book-detail', kwargs={'pk': book.id})
        response = self.client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        # assert "Note deleted successfully." in response.data

    def test_delete_book_as_regular_user(self):
        """Test: Regular user cannot delete books"""
        self.authenticate()
        book = Book.objects.create(name="Book10", author="Author1123",price=100,stock=10, user=self.superuser)
        url = reverse('book-detail', kwargs={'pk': book.id})
        response = self.client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Only superusers can create books." in response.data['detail']
