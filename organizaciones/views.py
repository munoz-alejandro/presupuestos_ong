from decimal import Decimal

from django.contrib import messages
from django.db import transaction
from django.db.models import DecimalField, OuterRef, Q, Subquery, Sum
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from django.urls import reverse_lazy

from .models import Donacion, LineaOrdenCompra, OrdenCompra, Presupuesto, Proyecto
from .forms import (
    DonacionForm,
    LineaOrdenCompraFormSet,
    OrdenCompraForm,
    PresupuestoForm,
    ProyectoForm,
)

def _nonzero_items(items):
    return [
        {"label": label, "count": count}
        for label, count in items
        if count
    ]

class SearchListMixin:
    search_param = "q"
    search_fields = []

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get(self.search_param, "").strip()

        if not query:
            return queryset

        filters = Q()
        for field in self.search_fields:
            filters |= Q(**{f"{field}__icontains": query})

        return queryset.filter(filters)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["q"] = self.request.GET.get(self.search_param, "").strip()
        return context

### Inicio

def home(request):
    return redirect("proyecto-list")

### Proyecto

class ProyectoListView(SearchListMixin, ListView):
    """ Listado de proyectos """
    model = Proyecto
    template_name = "proyectos/proyecto_list.html"
    context_object_name = "proyectos"
    search_fields = ["codigo", "nombre", "municipio", "departamento"]

class ProyectoCreateView(CreateView):
    """ Creación de proyectos """
    model = Proyecto
    form_class = ProyectoForm
    template_name = "proyectos/proyecto_create.html"
    success_url = reverse_lazy("proyecto-list")
    extra_context = {"title": "Crear Proyecto", "cancel_url": reverse_lazy("proyecto-list")}

    def form_valid(self, form):
        # Usamos la validación del form para enviar un mensaje al frontend y mostrarlo si todo va bien
        messages.success(self.request, "Proyecto creado exitosamente.")
        return super().form_valid(form)

class ProyectoUpdateView(UpdateView):
    """ Actualizacion de proyectos """
    model = Proyecto
    form_class = ProyectoForm
    template_name = "proyectos/proyecto_create.html"
    success_url = reverse_lazy("proyecto-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"Editar Proyecto {self.object.codigo}"
        context["cancel_url"] = reverse_lazy("proyecto-list")
        return context

    def form_valid(self, form):
        messages.success(self.request, "Proyecto actualizado exitosamente.")
        return super().form_valid(form)

class ProyectoDeleteView(DeleteView):
    model = Proyecto
    template_name = "proyectos/confimar_delete.html"
    success_url = reverse_lazy("proyecto-list")
    extra_context = {"title": "Eliminar Proyecto", "cancel_url": reverse_lazy("proyecto-list")}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cascade_items"] = _nonzero_items(
            [
                ("Presupuestos", self.object.presupuestos.count()),
                ("Donaciones", self.object.donaciones.count()),
                ("Ordenes de compra", self.object.ordenes_compra.count()),
                (
                    "Líneas de orden de compra",
                    LineaOrdenCompra.objects.filter(orden_compra__proyecto=self.object).count(),
                ),
            ]
        )
        return context

    def form_valid(self, form):
        messages.success(self.request, "Proyecto eliminado exitosamente.")
        return super().form_valid(form)


### Presupuesto

class PresupuestoListView(SearchListMixin, ListView):
    """ Listado de presupuestos """
    model = Presupuesto
    template_name = "presupuestos/presupuesto_list.html"
    context_object_name = "presupuestos"
    search_fields = ["proyecto__codigo", "proyecto__nombre", "rubro"]

class PresupuestoCreateView(CreateView):
    """ Creación de presupuestos """
    model = Presupuesto
    form_class = PresupuestoForm
    template_name = "presupuestos/presupuesto_create.html"
    success_url = reverse_lazy("presupuesto-list")
    extra_context = {"title": "Crear Presupuesto", "cancel_url": reverse_lazy("presupuesto-list")}

    def form_valid(self, form):
        messages.success(self.request, "Presupuesto creado exitosamente.")
        return super().form_valid(form)

class PresupuestoUpdateView(UpdateView):
    """ Actualizacion de presupuestos """
    model = Presupuesto
    form_class = PresupuestoForm
    template_name = "presupuestos/presupuesto_create.html"
    success_url = reverse_lazy("presupuesto-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"Editar Presupuesto {self.object}"
        context["cancel_url"] = reverse_lazy("presupuesto-list")
        return context

    def form_valid(self, form):
        messages.success(self.request, "Presupuesto actualizado exitosamente.")
        return super().form_valid(form)

class PresupuestoDeleteView(DeleteView):
    """ Eliminación de presupuestos """
    model = Presupuesto
    template_name = "presupuestos/confirmar_delete.html"
    success_url = reverse_lazy("presupuesto-list")
    extra_context = {"title": "Eliminar Presupuesto", "cancel_url": reverse_lazy("presupuesto-list")}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cascade_items"] = _nonzero_items(
            [
                ("Donaciones", self.object.donaciones.count()),
                ("Líneas de orden de compra", self.object.lineas_orden_compra.count()),
            ]
        )
        return context

    def form_valid(self, form):
        messages.success(self.request, "Presupuesto eliminado exitosamente.")
        return super().form_valid(form)


### Donacion

class DonacionListView(SearchListMixin, ListView):
    """ Listado de donaciones """
    model = Donacion
    template_name = "donaciones/donacion_list.html"
    context_object_name = "donaciones"
    search_fields = ["proyecto__codigo", "proyecto__nombre", "presupuesto__rubro", "donante"]

class DonacionCreateView(CreateView):
    """ Creación de donaciones """
    model = Donacion
    form_class = DonacionForm
    template_name = "donaciones/donacion_create.html"
    success_url = reverse_lazy("donacion-list")
    extra_context = {"title": "Crear Donación", "cancel_url": reverse_lazy("donacion-list")}

    def form_valid(self, form):
        messages.success(self.request, "Donación creada exitosamente.")
        return super().form_valid(form)

class DonacionUpdateView(UpdateView):
    """ Actualizacion de donaciones """
    model = Donacion
    form_class = DonacionForm
    template_name = "donaciones/donacion_create.html"
    success_url = reverse_lazy("donacion-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"Editar Donación {self.object}"
        context["cancel_url"] = reverse_lazy("donacion-list")
        return context

    def form_valid(self, form):
        messages.success(self.request, "Donación actualizada exitosamente.")
        return super().form_valid(form)

class DonacionDeleteView(DeleteView):
    """ Eliminación de donaciones """
    model = Donacion
    template_name = "donaciones/confirmar_delete.html"
    success_url = reverse_lazy("donacion-list")
    extra_context = {"title": "Eliminar Donación", "cancel_url": reverse_lazy("donacion-list")}

    def form_valid(self, form):
        messages.success(self.request, "Donación eliminada exitosamente.")
        return super().form_valid(form)


### Orden de Compra

class OrdenCompraListView(SearchListMixin, ListView):
    """ Listado de ordenes de compra """
    model = OrdenCompra
    template_name = "ordenes/ordencompra_list.html"
    context_object_name = "ordenes_compra"
    search_fields = ["proyecto__codigo", "proyecto__nombre", "proveedor", "descripcion"]

class OrdenCompraDeleteView(DeleteView):
    """ Eliminación de ordenes de compra """
    model = OrdenCompra
    template_name = "ordenes/confirmar_delete.html"
    success_url = reverse_lazy("ordencompra-list")
    extra_context = {"title": "Eliminar Orden de Compra", "cancel_url": reverse_lazy("ordencompra-list")}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cascade_items"] = _nonzero_items(
            [
                ("Líneas de orden de compra", self.object.lineas.count()),
            ]
        )
        return context

    def form_valid(self, form):
        messages.success(self.request, "Orden de compra eliminada exitosamente.")
        return super().form_valid(form)

def orden_compra_create(request):
    """ Creación de ordenes de compra con sus líneas """
    orden_compra = OrdenCompra()
    form = OrdenCompraForm(request.POST or None, instance=orden_compra)
    proyecto = _selected_proyecto(request, orden_compra)
    formset = LineaOrdenCompraFormSet(request.POST or None, instance=orden_compra, proyecto=proyecto)

    if request.method == "POST" and form.is_valid() and formset.is_valid():
        if _formset_matches_project(request, formset, form.cleaned_data["proyecto"]):
            with transaction.atomic():
                orden_compra = form.save()
                formset.instance = orden_compra
                formset.save()
            messages.success(request, "Orden de compra creada exitosamente.")
            return redirect("ordencompra-list")

    return render(
        request,
        "ordenes/ordencompra_form.html",
        {
            "title": "Crear Orden de Compra",
            "form": form,
            "formset": formset,
            "presupuestos_por_proyecto": _presupuestos_por_proyecto(),
            "cancel_url": reverse_lazy("ordencompra-list"),
        },
    )

def orden_compra_update(request, pk):
    """ Actualización de ordenes de compra con sus líneas """
    orden_compra = get_object_or_404(OrdenCompra, pk=pk)
    form = OrdenCompraForm(request.POST or None, instance=orden_compra)
    proyecto = _selected_proyecto(request, orden_compra)
    formset = LineaOrdenCompraFormSet(request.POST or None, instance=orden_compra, proyecto=proyecto)

    if request.method == "POST" and form.is_valid() and formset.is_valid():
        if _formset_matches_project(request, formset, form.cleaned_data["proyecto"]):
            with transaction.atomic():
                form.save()
                formset.save()
            messages.success(request, "Orden de compra actualizada exitosamente.")
            return redirect("ordencompra-list")

    return render(
        request,
        "ordenes/ordencompra_form.html",
        {
            "title": "Editar Orden de Compra",
            "form": form,
            "formset": formset,
            "presupuestos_por_proyecto": _presupuestos_por_proyecto(),
            "cancel_url": reverse_lazy("ordencompra-list"),
        },
    )

def _selected_proyecto(request, orden_compra):
    if request.method == "POST":
        return Proyecto.objects.filter(pk=request.POST.get("proyecto")).first()
    if orden_compra.proyecto_id:
        return orden_compra.proyecto
    return None

def _presupuestos_por_proyecto():
    presupuestos = Presupuesto.objects.select_related("proyecto").order_by("proyecto__codigo", "rubro")
    data = {}

    for presupuesto in presupuestos:
        data.setdefault(str(presupuesto.proyecto_id), []).append(
            {
                "id": presupuesto.id,
                "label": str(presupuesto),
            }
        )

    return data

def _formset_matches_project(request, formset, proyecto):
    is_valid = True
    has_line = False

    for form in formset:
        if not form.cleaned_data or form.cleaned_data.get("DELETE"):
            continue
        has_line = True
        presupuesto = form.cleaned_data.get("presupuesto")
        monto = form.cleaned_data.get("monto")
        if presupuesto and presupuesto.proyecto_id != proyecto.id:
            form.add_error("presupuesto", "El presupuesto debe pertenecer al proyecto seleccionado.")
            is_valid = False
            continue

        if presupuesto and monto:
            disponible = _disponible_presupuesto(presupuesto, formset.instance)
            if monto > disponible:
                form.add_error(
                    "monto",
                    f"No puede gastar más de lo disponible para este presupuesto: {disponible:,.2f}.",
                )
                is_valid = False

    if not has_line:
        messages.error(request, "Agregue al menos una línea de presupuesto.")
        is_valid = False

    return is_valid

def _disponible_presupuesto(presupuesto, orden_compra=None):
    donado = (
        Donacion.objects.filter(presupuesto=presupuesto).aggregate(total=Sum("monto"))["total"]
        or Decimal("0.00")
    )
    gastos = LineaOrdenCompra.objects.filter(presupuesto=presupuesto)

    if orden_compra and orden_compra.pk:
        gastos = gastos.exclude(orden_compra=orden_compra)

    gastado = gastos.aggregate(total=Sum("monto"))["total"] or Decimal("0.00")
    return donado - gastado

def disponibilidad_proyecto(request, pk):
    """ Disponibilidad de fondos por rubro de presupuesto """
    proyecto = get_object_or_404(Proyecto, pk=pk)
    donated_subquery = (
        Donacion.objects.filter(presupuesto=OuterRef("pk"))
        .values("presupuesto")
        .annotate(total=Sum("monto"))
        .values("total")
    )
    spent_subquery = (
        Presupuesto.objects.filter(pk=OuterRef("pk"))
        .values("pk")
        .annotate(total=Sum("lineas_orden_compra__monto"))
        .values("total")
    )
    decimal_field = DecimalField(max_digits=12, decimal_places=2)
    presupuestos = (
        proyecto.presupuestos.annotate(
            donado=Coalesce(
                Subquery(donated_subquery),
                Decimal("0.00"),
                output_field=decimal_field,
            ),
            gastado=Coalesce(
                Subquery(spent_subquery),
                Decimal("0.00"),
                output_field=decimal_field,
            ),
        )
        .order_by("rubro")
    )

    rows = [
        {
            "presupuesto": presupuesto,
            "donado": presupuesto.donado,
            "gastado": presupuesto.gastado,
            "disponible": presupuesto.donado - presupuesto.gastado,
        }
        for presupuesto in presupuestos
    ]

    return render(
        request,
        "proyectos/disponibilidad.html",
        {
            "proyecto": proyecto,
            "rows": rows,
        },
    )