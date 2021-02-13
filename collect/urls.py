from django.urls import path
from . import views
from . import api_view

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    #path('collect/<pk>', views.Detail.as_view(), name='detail'),
    path('collect/<pk>', views.detail, name='detail'),
    path('update/<pk>', views.update, name='update'),
    path('post/', views.add_post, name='post'),
    path('example/', views.ExampleList.as_view(), name='example'),
    path('collection/<username>', views.CollectList.as_view(), name='list'),
    #path('wish', views.WishList.as_view(), name='wish'),
    #path('collection/<username>/wish', views.UserWish.as_view(), name='user_wish'),
    path('category', views.CategoryList.as_view(), name='category'),
    #path('collection/<username>/category', views.UserCategory.as_view(), name='user_category'),
    path('place', views.PlaceList.as_view(), name='place'),
    path('nice', views.NiceList.as_view(), name='nice'),
    path('nice/<collect_pk>', views.NiceUser.as_view(), name='nicer'),
    path('download', views.download_page, name='download_page'),
    path('downloading', views.download, name='download'),
    path('search/', views.search, name='search'),
    # API
    path('category/api', api_view.CategoryAPI.as_view(), name='cat_api'),
    path('category/api/<pk>', api_view.CategoryRetAPI.as_view(), name='cat_api_pk'),
    path('place/api', api_view.PlaceAPI.as_view(), name='place_api'),
    path('place/api/<pk>', api_view.PlaceRetAPI.as_view(), name='place_api_pk'),
    path('post/api', api_view.CollectAPI.as_view(), name='post_api'),
    path('collect/api/<pk>', api_view.CollectRetAPI.as_view(), name='collect_api_pk'),
    path('photo/api', api_view.PhotoAPI.as_view(), name='photo_api'),
    path('collect/<collect_pk>/comment', api_view.CommentAPI.as_view(), name='collect_api'),
    path('collect/<comment_pk>/reply', api_view.ReplyAPI.as_view(), name='reply_api'),
    path('collect/<collect_pk>/nice', api_view.NiceAPI.as_view(), name='nice_api'),
    path('offer/<collect_pk>/', api_view.OfferAPI.as_view(), name='offer_api'),
]