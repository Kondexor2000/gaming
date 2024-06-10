"""
URL configuration for gaming project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path
from django.contrib import admin
from gamingapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('edit-profile/', views.EditProfileView.as_view(), name='edit_profile'),
    path('delete-account/', views.DeleteAccountView.as_view(), name='delete_account'),
    path('stores/<int:store_pk>/products/add', views.AddLaptopView.as_view(), name='product-list'),
    path('stores/<int:store_pk>/products/', views.search_laptops, name='product-list'),
    path('stores/<int:store_pk>/products/<int:product_pk>/update/', views.UpdateLaptopView.as_view(), name='product-update'),    
    path('stores/<int:store_pk>/products/<int:product_pk>/delete/', views.DeleteLaptopView.as_view(), name='product-delete'),
    path('stores/', views.StoreListView.as_view(), name='store-list'),
    path('stores/<int:pk>/', views.StoreDetailView.as_view(), name='store-detail'),
    path('stores/add', views.AddStoreView.as_view(), name='store-add'),
    path('stores/<int:store_pk>/products/<int:product_pk>/', views.display_first_record_with_lower_price, name='lower-prices'),
    path('stores/<int:store_pk>/products/<int:product_pk>/other', views.display_second_and_subsequent_records_with_lower_prices, name='lower-prices-other'),
    path('', views.search_stores_for_request_user, name='category'),
    path('search/', views.search_stores, name='search-products'),
]