from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

import store.views
import store.api_views

urlpatterns = [
    # API URLs
    path('api/v1/products/', store.api_views.ProductListView.as_view()),
    path('api/v1/products/create/', store.api_views.ProductCreateView.as_view()),
    path('api/v1/products/<int:id>/delete/', store.api_views.ProductDestroyView.as_view()),

    path('admin/', admin.site.urls),
    path('products/<int:id>/', store.views.show, name='show-product'),
    path('cart/', store.views.cart, name='shopping-cart'),
    path('', store.views.index, name='list-products'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
