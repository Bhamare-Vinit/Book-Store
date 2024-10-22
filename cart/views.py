from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Cart, CartItem
from book.models import Book
from .serializers import CartSerializer, CartItemSerializer
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from django.db import transaction

class CartViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def get_user_cart(self, user):
        """
        Fetch the active cart (is_ordered=False) for the logged-in user.
        If not found, create a new one.
        """
        cart, created = Cart.objects.get_or_create(user=user, is_ordered=False)
        return cart
    # @swagger_auto_schema(operation_description="Get Cart",request_body=CartSerializer, 
    #                      responses={
    #                          201: CartSerializer,
    #                          400: "Bad Request: Invalid input data.",
    #                          403: "Forbidden: Only authenticated users can access their cart.",
    #                          500: "Internal Server Error: An error occurred during Getting Cart"})
    def list(self, request):
        """
        GET request: List the user's active cart and its items.
        """
        try:
            cart = self.get_user_cart(request.user) 
            serializer = CartSerializer(cart)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except NotFound:
            return Response({
                "error": "Cart not found.",
                "detail": "No active cart found for the current user."
            }, status=status.HTTP_404_NOT_FOUND)
        except PermissionError as e:
            return Response({
                "error": "Permission denied.",
                "detail": f"You do not have the required permissions to access this cart, {str(e)}"
            }, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({
                "error": "An error occurred while retrieving the cart.",
                "detail": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(operation_description="Create Cart",request_body=CartSerializer, 
                         responses={
                             201: CartSerializer,
                             400: "Bad Request: Invalid input data.",
                             404: "Not Found: Book not found.",
                             500: "Internal Server Error: An error occurred during Creating Cart"})
    def create(self, request):
        """
        POST request: Add books to the user's active cart or update quantities.
        Request body should contain 'book_id' and 'quantity'.
        """
        user = request.user
        cart = self.get_user_cart(user)

        book_id = request.data.get('book_id')
        quantity = request.data.get('quantity')

        if not book_id or not quantity:
            raise ValidationError("Both 'book_id' and 'quantity' are required.")
        try:
            quantity = int(quantity)
            if quantity <= 0:
                raise ValidationError("Quantity must be a positive integer.")
        except ValueError:
            raise ValidationError("Quantity must be a valid integer.")

        try:
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            return Response({
                "error": "Book not found.",
                "detail": f"No book found with id {book_id}."
            }, status=status.HTTP_404_NOT_FOUND)

        try:
            with transaction.atomic():
                cart_item, created = CartItem.objects.get_or_create(cart=cart, book=book)

                # Update price and quantity
                cart_item.price = book.price * quantity
                cart_item.quantity = quantity
                cart_item.save()

                # Recalculate cart totals
                cart.total_quantity = sum(item.quantity for item in cart.items.all())
                cart.total_price = sum(item.price for item in cart.items.all())  # item.price is already price * quantity
                cart.save()

            return Response({
                "message": "Cart updated successfully.",
                "data": CartSerializer(cart).data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                "error": "An error occurred while updating the cart.",
                "detail": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @swagger_auto_schema(
            operation_description="Delete Item from Cart",
            request_body=CartSerializer,
            responses={
                201: CartSerializer,
                400: "Bad Request: Invalid input data.",
                404: "Not Found: Cart item not found.",
                500: "Internal Server Error: An error occurred during Deleting Item from Cart"})
    def destroy(self, request, pk=None):
        """
        DELETE request: Remove a specific cart item (pk) or clear the entire cart.
        After deleting, update the cart's total price and quantity.
        """
        cart = self.get_user_cart(request.user)
        try:
            if pk:
                try:
                    cart_item = CartItem.objects.get(cart=cart, id=pk)
                    cart_item.delete()
                except CartItem.DoesNotExist:
                    raise NotFound('Cart item not found.')
                cart.total_quantity = sum(item.quantity for item in cart.items.all())
                cart.total_price = sum(item.quantity * item.price for item in cart.items.all())
                cart.save()
            else:
                cart.items.all().delete()
                cart.total_price = 0
                cart.total_quantity = 0
                cart.save()
            return Response({"message": "Cart deleted successfully.",},status=status.HTTP_204_NO_CONTENT)
        except CartItem.DoesNotExist:
            return Response({
                "error": "Cart item not found.",
                "detail": "The specified cart item could not be found."
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "error": "An error occurred while deleting the item from the cart.",
                "detail": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

    @swagger_auto_schema(
            operation_description="Order Cart",request_body=CartSerializer,
            responses={
                201: CartSerializer,
                400: "Bad Request: Invalid input data.",
                404: "Not Found: Active cart not found.",
                500: "Internal Server Error: An error occurred during Ordering Cart"})
    @action(detail=False, methods=['patch'], url_path='order_cart', permission_classes=[IsAuthenticated])
    def order_cart(self, request):
        """
        PATCH request: Mark cart as ordered and update book stock.
        """
        try:
            cart = self.get_user_cart(request.user)

            if cart.is_ordered:
                return Response({
                    'error': 'This cart has already been ordered.'
                }, status=status.HTTP_400_BAD_REQUEST)
            if cart.items.count() == 0:
                return Response({
                    'error': 'Your cart is empty. Please add items before placing an order.'
                }, status=status.HTTP_400_BAD_REQUEST)
            for cart_item in cart.items.all():
                book = cart_item.book
                if book.stock < cart_item.quantity:
                    return Response({
                        'error': f'Not enough stock for {book.name}. Available stock: {book.stock}'
                    }, status=status.HTTP_400_BAD_REQUEST)
                book.stock -= cart_item.quantity
                book.save()
            cart.is_ordered = True
            cart.save()

            return Response({
                'message': 'Cart has been successfully ordered.',
                'cart': CartSerializer(cart).data
            }, status=status.HTTP_200_OK)

        except Cart.DoesNotExist:
            return Response({
                'error': 'Active cart not found.'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
            operation_description="Delete Complete Cart",
            request_body=CartSerializer,
            responses={
                201: CartSerializer,
                400: "Bad Request: Invalid input data.",
                404: "Not Found: Active cart not found.",
                500: "Internal Server Error: An error occurred during Deleteing Cart"})   
    @action(detail=False, methods=['delete'], url_path='delete_cart', permission_classes=[IsAuthenticated])
    def delete_cart(self, request):
        """
        DELETE request: Delete the user's active cart and all its items.
        """
        try:
            cart = self.get_user_cart(request.user)
            
            # cart.items.all().delete()

            cart.delete()

            return Response({
                'message': 'Cart and all its items have been successfully deleted.'
            }, status=status.HTTP_204_NO_CONTENT)

        except Cart.DoesNotExist:
            return Response({
                'error': 'Active cart not found.'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': 'An error occurred during deleting the cart.',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


