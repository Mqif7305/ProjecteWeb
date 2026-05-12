"""
URL configuration for projecte project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from projecte.games import views as game_views, views
from projecte.games.views import SignUpView


urlpatterns = [
    path('', game_views.home, name='home'),
    path('accounts/signup/', SignUpView.as_view(), name='signup'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls),
    path('juegos/', game_views.lista_juegos, name='lista_juegos'),
    path('game/<int:id>/', views.game_detail, name='game_detail'),
    path('search/', game_views.search_juegos, name='search_juegos'),
    path('wishlist/toggle/<int:id>/', views.toggle_wishlist, name='toggle_wishlist'),
    path('profile/', views.profile_view, name='profile'),
    path('comment/edit/<int:pk>/', views.edit_comment, name='edit_comment'),
    path('comment/delete/<int:pk>/', views.delete_comment, name='delete_comment'),
]
