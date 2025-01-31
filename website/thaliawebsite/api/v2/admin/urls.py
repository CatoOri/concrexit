from django.urls import path, include

app_name = "thaliawebsite"

urlpatterns = [
    path("", include("events.api.v2.admin.urls")),
    path("", include("payments.api.v2.admin.urls")),
    path("", include("sales.api.v2.admin.urls")),
    path("", include("pizzas.api.v2.admin.urls")),
]
