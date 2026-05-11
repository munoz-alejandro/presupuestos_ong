from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("proyectos/", views.ProyectoListView.as_view(), name="proyecto-list"),
    path("proyectos/crear/", views.ProyectoCreateView.as_view(), name="proyecto-create"),
    path("proyectos/<int:pk>/editar/", views.ProyectoUpdateView.as_view(), name="proyecto-update"),
    path("proyectos/<int:pk>/eliminar/", views.ProyectoDeleteView.as_view(), name="proyecto-delete"),
    path("proyectos/<int:pk>/disponibilidad/", views.disponibilidad_proyecto, name="proyecto-disponibilidad"),
    path("presupuestos/", views.PresupuestoListView.as_view(), name="presupuesto-list"),
    path("presupuestos/crear/", views.PresupuestoCreateView.as_view(), name="presupuesto-create"),
    path("presupuestos/<int:pk>/editar/", views.PresupuestoUpdateView.as_view(), name="presupuesto-update"),
    path("presupuestos/<int:pk>/eliminar/", views.PresupuestoDeleteView.as_view(), name="presupuesto-delete"),
    path("donaciones/", views.DonacionListView.as_view(), name="donacion-list"),
    path("donaciones/crear/", views.DonacionCreateView.as_view(), name="donacion-create"),
    path("donaciones/<int:pk>/editar/", views.DonacionUpdateView.as_view(), name="donacion-update"),
    path("donaciones/<int:pk>/eliminar/", views.DonacionDeleteView.as_view(), name="donacion-delete"),
    path("ordenes/", views.OrdenCompraListView.as_view(), name="ordencompra-list"),
    path("ordenes/crear/", views.orden_compra_create, name="ordencompra-create"),
    path("ordenes/<int:pk>/editar/", views.orden_compra_update, name="ordencompra-update"),
    path("ordenes/<int:pk>/eliminar/", views.OrdenCompraDeleteView.as_view(), name="ordencompra-delete"),
]
