from decimal import Decimal

from django import forms
from django.forms import BaseInlineFormSet, inlineformset_factory
from django.utils import timezone

from .models import Donacion, LineaOrdenCompra, OrdenCompra, Presupuesto, Proyecto
from .constants import MUNICIPIOS_POR_DEPARTAMENTO

# Formato de la fecha, aseguramos usar dia-mes-año
DATE_INPUT_FORMATS = ["%d-%m-%Y", "%d/%m/%Y", "%d%m%Y"]


#### Custom Widgets 

class DayMonthYearDateInput(forms.DateInput):
    """ Input para la fecha, aseguramos usar dia-mes-año """
    def __init__(self, *args, **kwargs):
        attrs = kwargs.pop("attrs", {})
        attrs.setdefault("placeholder", "dd-mm-yyyy")
        attrs.setdefault("inputmode", "numeric")
        attrs.setdefault("maxlength", "10")
        attrs.setdefault("pattern", r"\d{2}[-/]?\d{2}[-/]?\d{4}")
        attrs.setdefault("title", "Use dd-mm-yyyy, dd/mm/yyyy, or ddmmyyyy.")
        attrs.setdefault("data-date-input", "day-month-year")
        super().__init__(*args, format="%d-%m-%Y", attrs=attrs, **kwargs)

class BootstrapFormMixin:
    """ Mixin para agregar clases de Bootstrap a los campos del formulario, de forma automática """
    def _style_fields(self):
        for field in self.fields.values():
            css_class = "form-select" if isinstance(field.widget, forms.Select) else "form-control"
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing} {css_class}".strip()

#### Proyecto

class ProyectoForm(BootstrapFormMixin, forms.ModelForm):
    """ Formulario para el modelo Proyecto """
    municipios_por_departamento = MUNICIPIOS_POR_DEPARTAMENTO

    municipio = forms.ChoiceField(
        choices=[("", "Seleccione un departamento primero")]
    )
    fecha_inicio = forms.DateField(
        input_formats=DATE_INPUT_FORMATS,
        widget=DayMonthYearDateInput
        )
    fecha_final = forms.DateField(
        input_formats=DATE_INPUT_FORMATS,
        widget=DayMonthYearDateInput
        )

    class Meta:
        model = Proyecto
        fields = ["nombre", "departamento", "municipio",  "fecha_inicio", "fecha_final"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        departamento = self.data.get("departamento") or self.initial.get("departamento")
        if not departamento and self.instance.pk:
            departamento = self.instance.departamento

        self.fields["municipio"].choices = self._municipio_choices(departamento)
        self._style_fields()

    def _municipio_choices(self, departamento):
        municipios = MUNICIPIOS_POR_DEPARTAMENTO.get(departamento, [])
        placeholder = "Seleccione un municipio" if municipios else "Seleccione un departamento primero"
        return [("", placeholder), *[(municipio, municipio) for municipio in municipios]]

    def clean_municipio(self):
        municipio = self.cleaned_data["municipio"]
        departamento = self.cleaned_data.get("departamento")
        municipios = MUNICIPIOS_POR_DEPARTAMENTO.get(departamento, [])

        if municipio not in municipios:
            raise forms.ValidationError("Seleccione un municipio válido para el departamento.")

        return municipio

#### Presupuesto

class PresupuestoForm(BootstrapFormMixin, forms.ModelForm):
    """ Formulario para el modelo Presupuesto """
    presupuesto = forms.DecimalField(
        decimal_places=2,
        localize=False,  # Para usar . en separador decimal
        max_digits=10,
        min_value=0,
        widget=forms.NumberInput(attrs={"step": "0.01"}),
    )

    class Meta:
        model = Presupuesto
        fields = ["proyecto", "rubro", "presupuesto"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style_fields()

    def clean(self):
        cleaned_data = super().clean()
        proyecto = cleaned_data.get("proyecto")
        rubro = cleaned_data.get("rubro")

        if proyecto and rubro:
            duplicate = Presupuesto.objects.filter(proyecto=proyecto, rubro__iexact=rubro)
            if self.instance.pk:
                duplicate = duplicate.exclude(pk=self.instance.pk)
            if duplicate.exists():
                raise forms.ValidationError("Este rubro ya existe para el proyecto seleccionado.")

        return cleaned_data

#### Donacion

class DonacionForm(BootstrapFormMixin, forms.ModelForm):
    """ Formulario para el modelo Donacion """
    fecha = forms.DateField(
        input_formats=DATE_INPUT_FORMATS,
        widget=DayMonthYearDateInput(),
    )
    monto = forms.DecimalField(
        decimal_places=2,
        localize=False,  # Para usar . en separador decimal
        max_digits=12,
        min_value=Decimal("0.01"),
        widget=forms.NumberInput(attrs={"step": "0.01"}),
    )

    class Meta:
        model = Donacion
        fields = ["proyecto", "presupuesto", "fecha", "donante", "monto"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style_fields()

    def clean(self):
        cleaned_data = super().clean()
        proyecto = cleaned_data.get("proyecto")
        presupuesto = cleaned_data.get("presupuesto")

        if proyecto and proyecto.fecha_final < timezone.localdate():
            self.add_error("proyecto", "No se puede registrar una donación para un proyecto vencido.")

        if proyecto and presupuesto and presupuesto.proyecto_id != proyecto.id:
            self.add_error("presupuesto", "El presupuesto debe pertenecer al proyecto seleccionado.")

        return cleaned_data

#### Orden de Compra

class OrdenCompraForm(BootstrapFormMixin, forms.ModelForm):
    """ Formulario para el modelo OrdenCompra """
    fecha = forms.DateField(
        input_formats=DATE_INPUT_FORMATS,
        widget=DayMonthYearDateInput(),
    )

    class Meta:
        model = OrdenCompra
        fields = ["proyecto", "fecha", "proveedor", "descripcion"]
        widgets = {
            "descripcion": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style_fields()


class LineaOrdenCompraForm(BootstrapFormMixin, forms.ModelForm):
    """ Formulario para las líneas de una orden de compra """
    monto = forms.DecimalField(
        decimal_places=2,
        localize=False,  # Para usar . en separador decimal
        max_digits=12,
        min_value=Decimal("0.01"),
        widget=forms.NumberInput(attrs={"step": "0.01"}),
    )

    class Meta:
        model = LineaOrdenCompra
        fields = ["presupuesto", "monto"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style_fields()


class BaseLineaOrdenCompraFormSet(BaseInlineFormSet):
    """ Validaciones compartidas para las líneas de orden de compra """
    def __init__(self, *args, proyecto=None, **kwargs):
        self.proyecto = proyecto
        super().__init__(*args, **kwargs)

        queryset = Presupuesto.objects.filter(proyecto=proyecto) if proyecto else Presupuesto.objects.none()
        for form in self.forms:
            form.fields["presupuesto"].queryset = queryset

    def clean(self):
        super().clean()
        seen_presupuestos = set()

        for form in self.forms:
            if not hasattr(form, "cleaned_data"):
                continue
            if not form.cleaned_data or form.cleaned_data.get("DELETE"):
                continue

            presupuesto = form.cleaned_data.get("presupuesto")
            if presupuesto is None:
                continue
            if presupuesto.id in seen_presupuestos:
                raise forms.ValidationError("Cada presupuesto solo puede usarse una vez por orden de compra.")
            seen_presupuestos.add(presupuesto.id)


LineaOrdenCompraFormSet = inlineformset_factory(
    OrdenCompra,
    LineaOrdenCompra,
    form=LineaOrdenCompraForm,
    formset=BaseLineaOrdenCompraFormSet,
    extra=1,
    can_delete=True,
)