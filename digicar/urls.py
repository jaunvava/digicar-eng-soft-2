from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="DigiCAR API",
        default_version="v1",
        description="Documentação das rotas de API do sistema DigiCAR",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="suporte@digi.com.br"),
        license=openapi.License(name="Private License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls", namespace="core")),
    path("clientes/", include("clientes.urls", namespace="clientes")),
    path("produtos/", include("produtos.urls", namespace="produtos")),
    path("financeiro/", include("financeiro.urls", namespace="financeiro")),
    path("orcamentos/", include("orcamentos.urls", namespace="orcamentos")),
    path("ordens/", include("ordens.urls", namespace="ordens")),
    path("relatorios/", include("relatorios.urls", namespace="relatorios")),
    path("fornecedores/", include("fornecedores.urls", namespace="fornecedores")),
    # Swagger API Documentation
    path(
        "swagger<format>/", schema_view.without_ui(cache_timeout=0), name="schema-json"
    ),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Customização do Admin
admin.site.site_header = "Administração do DigiCAR"
admin.site.site_title = "DigiCAR Admin"
admin.site.index_title = "Bem-vindo à Administração do DigiCAR"
