from django.urls import path
from store import views


urlpatterns = [
    path('store/',views.store, name = "store"),
    path('cart/',views.cart, name = "cart"),
    path('',views.handlelogin, name = "handlelogin"),
    path('logout/',views.handlelogout, name = "handlelogout"),
    path('signup/',views.signup, name = "signup"),
    path('checkout/',views.checkout, name = "checkout"),
    path('success/',views.success, name = "success"),
    path('update_item/',views.updateItem, name = "update_item"),
    path('process_order/',views.processOrder, name = "process_order")
]