from django.urls import path

from heyurl import views

urlpatterns = [
    path('', views.short_url, name='short_url'),
    path('store/', views.store, name='store'),
    path('/data/', views.data_panel, name='data')
]
