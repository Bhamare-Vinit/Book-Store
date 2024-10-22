from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from .models import Book
from .serializers import BookSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound, ValidationError,PermissionDenied
from django.core.exceptions import PermissionDenied
from rest_framework.decorators import action
from drf_yasg.utils import swagger_auto_schema

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all() 
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]  

    # 1. List all books (only accessible by authenticated users)
    # @swagger_auto_schema(
    #         operation_description="Get all books",request_body=BookSerializer, 
    #         responses={
    #             201: BookSerializer,
    #             400: "Bad Request: Invalid input data.",
    #             403: "Forbidden: Only authenticated users can view books.",
    #             500: "Internal Server Error: An error occurred during Adding Book"})
    def list(self, request, *args, **kwargs):
        """
        List all books. Only authenticated users can view books.
        """
        try:
            books = self.queryset
            serializer = self.get_serializer(books, many=True) 
            # return Response(serializer.data, status=status.HTTP_200_OK)
            return Response({
                "message": "Notes retrieved successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except PermissionError as e:
            return Response({
                "error": "Permission denied.",
                "detail": f"You do not have the required permissions to view this resource, {str(e)}"
            }, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            # logger.error(f"Error in list method: {e}")
            return Response({
                "error": "An error occurred while retrieving notes.",
                "detail": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        

    @swagger_auto_schema(
            operation_description="Add a new book",request_body=BookSerializer, 
            responses={
                201: BookSerializer,
                400: "Bad Request: Invalid input data.",
                403: "Forbidden: Only superusers can create books.",
                500: "Internal Server Error: An error occurred during Adding Book"})
    def create(self, request, *args, **kwargs):
        """
        Only superusers are allowed to create books.
        Save the book with the logged-in superuser as the owner.
        """
        try:
            if not request.user.is_superuser: 
                raise PermissionDenied("Only superusers can create books.")
            
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user)
            headers = self.get_success_headers(serializer.data)
            return Response({
                "message": "Note created successfully.",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED, headers=headers)
            # return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except PermissionError as e:
            return Response({
                "error": "Permission denied.",
                "detail": f"You do not have the required permissions to to add new book, {str(e)}"
            }, status=status.HTTP_403_FORBIDDEN)
        except ValidationError as e:
            return Response({
                "error": "Invalid data.",
                "detail": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # logger.error(f"Error in create method: {e}")
            return Response({
                "error": "An error occurred while creating the note.",
                "detail": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            
            return Response({
                'user': request.user.email,
                'message': 'Book retrieved successfully.',
                'data': serializer.data
            }, status=status.HTTP_200_OK)

        except NotFound:
            return Response({
                'user': request.user.email,
                'error': 'Book not found.',
                'detail': 'The book with the provided ID does not exist.'
            }, status=status.HTTP_404_NOT_FOUND)
        except PermissionError as e:
            return Response({
                "error": "Permission denied.",
                "detail": f"You do not have the required permissions to to get this book, {str(e)}"
            }, status=status.HTTP_403_FORBIDDEN)
        except ValidationError as e:
            return Response({
                "error": "Invalid data.",
                "detail": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'user': request.user.email,
                'error': 'An error occurred while retrieving the book.',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        
    @swagger_auto_schema(
            operation_description="Add a new book",request_body=BookSerializer, 
            responses={
                201: BookSerializer,
                400: "Bad Request: Invalid input data.",
                403: "Forbidden: Permission denied.",
                404: "Not Found: The book with the provided ID does not exist.",
                500: "Internal Server Error: An error occurred during updating Book"})
    def update(self, request, pk=None, *args, **kwargs):
        partial = False
        try:
            if not request.user.is_superuser:
                raise PermissionDenied("Only superusers can create books.")
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response({
                'user': request.user.email,
                'message': 'Note updated successfully.',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except ValidationError as e:
            # logger.error(f"Validation failed: {e.detail}")
            return Response({
                'user': request.user.email,
                'error': 'Validation failed.',
                'detail': e.detail
            }, status=status.HTTP_400_BAD_REQUEST)
        except NotFound:
            # logger.error(f"Note not found for user: {request.user.email}")
            return Response({
                'user': request.user.email,
                'error': 'Note not found.',
                'detail': 'The note with the provided ID does not exist.'
            }, status=status.HTTP_404_NOT_FOUND)
        except PermissionDenied as e:
            # logger.error(f"Permission denied: {str(e)}")
            return Response({
                'user': request.user.email,
                'error': 'Permission denied.',
                'detail': str(e)
            }, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            # logger.error(f"An error occurred while updating the note: {str(e)}")
            return Response({
                'user': request.user.email,
                'error': 'An error occurred while updating the note.',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
            operation_description="Add a new book",request_body=BookSerializer, 
            responses={
                201: BookSerializer,
                400: "Bad Request: Invalid input data.",
                403: "Forbidden: Permission denied.",
                404: "Not Found: The book with the provided ID does not exist.",
                500: "Internal Server Error: An error occurred during updating Book"})
    def partial_update(self, request, pk=None, *args, **kwargs):
        partial = True
        try:
            if not request.user.is_superuser: 
                raise PermissionDenied("Only superusers can create books.")
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            # self.perform_update(serializer)
            serializer.save()
            return Response({
                'user': request.user.email,
                'message': 'Note partially updated successfully.',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({
                'user': request.user.email,
                'error': 'Validation failed.',
                'detail': e.detail
            }, status=status.HTTP_400_BAD_REQUEST)
        except NotFound:
            return Response({
                'user': request.user.email,
                'error': 'Note not found.',
                'detail': 'The note with the provided ID does not exist.'
            }, status=status.HTTP_404_NOT_FOUND)
        except PermissionDenied as e:
            return Response({
                'user': request.user.email,
                'error': 'Permission denied.',
                'detail': str(e)
            }, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({
                'user': request.user.email,
                'error': 'An error occurred while partially updating the note.',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
            operation_description="Add a new book",request_body=BookSerializer, 
            responses={
                204: BookSerializer,
                400: "Bad Request: An error occurred while deleting the book.",
                403: "Forbidden: Permission denied.",
                404: "Not Found: The book with the provided ID does not exist.",
                500: "Internal Server Error: An unexpected error occurred."})
    def destroy(self, request, pk=None, *args, **kwargs):
        try:
            if not request.user.is_superuser: 
                raise PermissionDenied("Only superusers can create books.")
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response({
                'user': request.user.email,
                'message': 'Note deleted successfully.'
            }, status=status.HTTP_204_NO_CONTENT)
        except NotFound:
            return Response({
                'user': request.user.email,
                'error': 'Note not found.',
                'detail': 'The note with the provided ID does not exist.'
            }, status=status.HTTP_404_NOT_FOUND)
        except PermissionDenied as e:
            return Response({
                'user': request.user.email,
                'error': 'Permission denied.',
                'detail': str(e)
            }, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({
                'user': request.user.email,
                'error': 'An error occurred while deleting the note.',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)