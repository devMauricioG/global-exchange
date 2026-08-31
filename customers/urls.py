from django.urls import path
from . import views

app_name = 'customers'

urlpatterns = [
    # Vistas Web (CBVs)
    path('', views.ClienteListView.as_view(), name='cliente-list'),
    path('nuevo/', views.ClienteCreateView.as_view(), name='cliente-create'),
    path('<int:pk>/', views.ClienteDetailView.as_view(), name='cliente-detail'),
    path('<int:pk>/editar/', views.ClienteUpdateView.as_view(), name='cliente-update'),
    path('<int:pk>/eliminar/', views.ClienteDeleteView.as_view(), name='cliente-delete'),

    # Endpoints API REST (JSON)
    path('api/', views.ClienteListCreateAPIView.as_view(), name='api-cliente-list-create'),
    path('api/<int:pk>/', views.ClienteDetailAPIView.as_view(), name='api-cliente-detail'),
    path('api/documento/<str:documento_ruc>/', views.ClienteDetailAPIView.as_view(), name='api-cliente-by-doc'),
]
