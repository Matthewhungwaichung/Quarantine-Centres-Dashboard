from django.urls import path
from orders import views


urlpatterns = [
    path('dashboard3', views.view_data_date)
]
