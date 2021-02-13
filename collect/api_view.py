from django.shortcuts import render, redirect, get_object_or_404
from .models import Category, Place, Collect, Photo, Comment, Reply, Nice
from user.models import User
from django.contrib.auth.mixins import LoginRequiredMixin as LR, UserPassesTestMixin as UP
from django.db.models import Count, Q
import string, random
from django.utils import timezone

#api
from .serializers import (
    UserSerializer, CategorySerializer, PlaceSerializer, CollectSerializer,
    PhotoSerializer, CommentSerializer, ReplySerializer, CollectOtherSerializer,
    OfferSerializer
)
from rest_framework import status, views, permissions
from rest_framework.response import Response

class CollectPermission(permissions.BasePermission):
    message = 'You are not a owner!'
    def has_object_permission(self, request, view, collect):
        return collect.user == request.user

class CategoryPermission(permissions.BasePermission):
    message = 'You are not a owner!'
    def has_object_permission(self, request, view, category):
        return category.user == request.user

class PlacePermission(permissions.BasePermission):
    message = 'You are not a owner!'
    def has_object_permission(self, request, view, place):
        return place.user == request.user

# add category with api
class CategoryAPI(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, format=None):
        user = self.request.user
        categories = Category.objects.filter(user=user).order_by('pk')
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        user = self.request.user
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# category retrieve api
class CategoryRetAPI(views.APIView):
    permission_classes = [permissions.IsAuthenticated, CategoryPermission]
    def get_object(self, pk):
        try:
            return Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            raise Http404
        
    def delete(self, request, pk, format=None):
        category = self.get_object(pk)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self, request, pk, format=None):
        category = self.get_object(pk)
        user = self.request.user
        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save(user=user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# add place with api
class PlaceAPI(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, format=None):
        user = self.request.user
        places = Place.objects.filter(user=user).order_by('pk')
        serializer = PlaceSerializer(places, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        user = self.request.user
        serializer = PlaceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# place retrieveve api
class PlaceRetAPI(views.APIView):
    permission_classes = [permissions.IsAuthenticated, PlacePermission]
    def get_object(self, pk):
        try:
            return Place.objects.get(pk=pk)
        except Place.DoesNotExist:
            raise Http404
    
    def delete(self, request, pk, format=None):
        place = self.get_object(pk)
        place.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self, request, pk, format=None):
        place = self.get_object(pk)
        user = self.request.user
        serializer = PlaceSerializer(place, data=request.data)
        if serializer.is_valid():
            serializer.save(user=user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CollectAPI(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    slug = ''.join(random.choice(string.ascii_letters + string.digits + '-_') for _ in range(8))
    """
    def get(self, request, format=None):
        collect = Collect.objects.all()
        serializer = CollectSerializer(collect, many=True)
        return Response(serializer.data)
    """
    def post(self, request, format=None):
        user = self.request.user
        slug = ''.join(random.choice(string.ascii_letters + string.digits + '-_') for _ in range(8))
        serializer = CollectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.posted = timezone.now
            serializer.save(id=slug, user=user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PhotoAPI(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, format=None):
        #collect = self.get_object(pk)
        serializer = PhotoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CollectRetAPI(views.APIView):
    permission_classes = [permissions.IsAuthenticated, CollectPermission]
    def get_object(self, pk):
        try:
            return Collect.objects.get(pk=pk)
        except Collect.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        collect = self.get_object(pk)
        serializer = CollectOtherSerializer(collect, many=False)
        return Response(serializer.data)
        
    def delete(self, request, pk, format=None):
        collect = self.get_object(pk)
        collect.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CommentAPI(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get_object(self, collect_pk):
        try:
            return Collect.objects.get(pk=collect_pk)
        except Collect.DoesNotExist:
            raise Http404

    def get(self, request, collect_pk, format=None):
        collect = self.get_object(collect_pk)
        comments = Comment.objects.filter(collect=collect).order_by('-posted')
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, collect_pk, format=None):
        user = self.request.user
        collect = self.get_object(collect_pk)
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(collect=collect, user=user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ReplyAPI(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get_object(self, comment_pk):
        try:
            return Comment.objects.get(pk=comment_pk)
        except Comment.DoesNotExist:
            raise Http404

    def post(self, request, comment_pk, format=None):
        user = self.request.user
        comment = self.get_object(comment_pk)
        serializer = ReplySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(comment=comment, user=user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class NiceAPI(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get_object(self, collect_pk):
        try:
            return Collect.objects.get(pk=collect_pk)
        except Collect.DoesNotExist:
            raise Http404

    def get(self, request, collect_pk, format=None):
        collect = self.get_object(collect_pk)
        user = self.request.user
        nice = Nice.objects.filter(user=user, collect=collect).count()
        if nice > 0:
            nicing = Nice.objects.get(user=user, collect=collect)
            nicing.delete()
            collect.nice_num -= 1
            collect.save()
        else:
            Nice.objects.create(collect=collect, user=user)
            collect.nice_num += 1
            collect.save()
        counts = Nice.objects.filter(collect=collect).count()
        data = {
            'counts': counts,
        }
        return Response(data)

class OfferAPI(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get_object(self, collect_pk):
        try:
            return Collect.objects.get(pk=collect_pk)
        except Collect.DoesNotExist:
            raise Http404

    def post(self, request, collect_pk, format=None):
        target_col = self.get_object(collect_pk)
        serializer = OfferSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(target_col=target_col)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)