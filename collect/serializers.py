from rest_framework import serializers
from .models import Category, Place, Photo, Collect, Comment, Reply, Tag, Nice, Offer
from user.models import User

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['text']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['pk', 'username', 'name', 'picture']

class CategorySerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)
    class Meta:
        model = Category
        fields = ['pk', 'name', 'user']

class PlaceSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)
    class Meta:
        model = Place
        fields = ['pk', 'name', 'user']

#for owner
class CollectSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)
    category = CategorySerializer(many=False, read_only=True)
    category_pk = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category', allow_null=True)
    place = PlaceSerializer(many=False, read_only=True)
    place_pk = serializers.PrimaryKeyRelatedField(
        queryset=Place.objects.all(),
        source='place', allow_null=True)
    class Meta:
        model = Collect
        fields = [
            'id', 'name', 'product_name', 'maker', 'num', 'saved', 'posted',
            'explain', 'acq_day', 'acq_place', 'price', 'user', 'category',
            'place', 'public', 'state', 'category_pk', 'place_pk'
        ]

#for every one
class CollectOtherSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)
    category = CategorySerializer(many=False, read_only=True)
    class Meta:
        model = Collect
        fields = [
            'id', 'name', 'product_name', 'maker', 'num', 'saved', 'posted',
            'explain', 'acq_day', 'acq_place', 'price', 'user', 'category',
            'public', 'state'
        ]

class PhotoSerializer(serializers.ModelSerializer):
    collect = CollectSerializer(many=False, read_only=True)
    collect_pk = serializers.PrimaryKeyRelatedField(
        queryset=Collect.objects.all(),
        source='collect'
    )
    class Meta:
        model = Photo
        fields = ['photo', 'collect', 'collect_pk']

class CommentSerializer(serializers.ModelSerializer):
    collect = CollectOtherSerializer(many=False, read_only=True)
    user = UserSerializer(many=False, read_only=True)
    class Meta:
        model = Comment
        fields = ['pk', 'content', 'collect', 'user', 'posted']

class ReplySerializer(serializers.ModelSerializer):
    comment = CommentSerializer(many=False, read_only=True)
    user = UserSerializer(many=False, read_only=True)
    class Meta:
        model = Reply
        fields = ['pk', 'content', 'comment', 'user', 'posted']

class NiceSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)
    collect = CollectOtherSerializer(many=False, read_only=True)
    class Meta:
        model = Nice
        fields = ['pk', 'collect', 'user']

class OfferSerializer(serializers.ModelSerializer):
    rec_col = CollectOtherSerializer(many=False, read_only=True)
    rec_col_pk = serializers.PrimaryKeyRelatedField(
        queryset=Collect.objects.all(),
        source='rec_col', allow_null=False)
    target_col = CollectOtherSerializer(many=False, read_only=True)
    target_col_pk = serializers.PrimaryKeyRelatedField(
        queryset=Collect.objects.all(),
        source='target_col', allow_null=False)
    class Meta:
        model = Offer
        fields = ['rec_col', 'target_col', 'rec_col_pk', 'target_col_pk']