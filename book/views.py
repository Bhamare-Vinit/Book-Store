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

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()  # Fetch all books
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]  # JWT token required for all actions

    # 1. List all books (only accessible by authenticated users)
    def list(self, request, *args, **kwargs):
        """
        List all books. Only authenticated users can view books.
        """
        books = self.queryset  # Get all books
        serializer = self.get_serializer(books, many=True)  # Serialize all book records
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def create(self, request, *args, **kwargs):
        """
        Only superusers are allowed to create books.
        Save the book with the logged-in superuser as the owner.
        """
        if not request.user.is_superuser:  # Check if the user is a superuser
            raise PermissionDenied("Only superusers can create books.")
        
        # Proceed with saving the book with the superuser as the owner
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)  # Automatically set the user as the book creator
        headers = self.get_success_headers(serializer.data)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    def retrieve(self, request, pk=None, *args, **kwargs):
        try:
            # Fetch the book instance by its primary key (ID)
            instance = self.get_object()
            
            # Serialize the book instance
            serializer = self.get_serializer(instance)
            
            # Return the response with the book data and a custom message
            return Response({
                'user': request.user.email,
                'message': 'Book retrieved successfully.',
                'data': serializer.data
            }, status=status.HTTP_200_OK)

        except NotFound:
            # Return a 404 response if the book is not found
            return Response({
                'user': request.user.email,
                'error': 'Book not found.',
                'detail': 'The book with the provided ID does not exist.'
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            # Return a 400 response for any other exception
            return Response({
                'user': request.user.email,
                'error': 'An error occurred while retrieving the book.',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None, *args, **kwargs):
        partial = False
        try:
            if not request.user.is_superuser:  # Check if the user is a superuser
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
        
    def partial_update(self, request, pk=None, *args, **kwargs):
        partial = True
        try:
            if not request.user.is_superuser:  # Check if the user is a superuser
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
        
    def destroy(self, request, pk=None, *args, **kwargs):
        try:
            if not request.user.is_superuser:  # Check if the user is a superuser
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