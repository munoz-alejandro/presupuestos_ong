from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum

from .constants import DEPARTAMENTOS_GUATEMALA
# Create your models here.


class Proyecto(models.Model):
    """ Modelo para el proyecto """
    codigo = models.CharField(max_length=6, unique=True, editable=False)
    nombre = models.CharField(max_length=200)
    municipio = models.CharField(max_length=120)
    departamento = models.CharField(max_length=120, choices=DEPARTAMENTOS_GUATEMALA)
    fecha_inicio = models.DateField()
    fecha_final = models.DateField()

    class Meta:
        ordering = ["codigo"]
    
    def save(self, *args, **kwargs):
        if not self.codigo:
            self.codigo = self.siguiente_codigo()
        super().save(*args, **kwargs)

    @classmethod
    def siguiente_codigo(cls):
        """ Método para obtener el siguiente código de proyecto, unico y automático """
        ultimo_proyecto = cls.objects.exclude(codigo="").order_by("-id").first()
        if ultimo_proyecto is None:
            siguiente_numero = 1
        else:
            siguiente_numero = int(ultimo_proyecto.codigo.split("-")[1])+1
        return f"P-{siguiente_numero:04d}"

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

class Presupuesto(models.Model):
    """ Modelo para el presupuesto """
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name="presupuestos")
    rubro = models.CharField(max_length=120)
    presupuesto = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        """ Meta para el presupuesto, forzamos que el presupuesto sea único por proyecto y rubro """
        ordering = ["proyecto__codigo", "rubro"]
        constraints = [
            models.UniqueConstraint(fields=["proyecto", "rubro"], name="unique_presupuesto_rubro_por_proyecto")
        ]

    def __str__(self):
        return f"{self.proyecto.codigo} - {self.rubro}"


class Donacion(models.Model):
    """ Modelo para registrar donaciones por proyecto y rubro de presupuesto """
    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        related_name="donaciones",
    )
    presupuesto = models.ForeignKey(
        Presupuesto,
        on_delete=models.CASCADE,
        related_name="donaciones",
    )
    fecha = models.DateField()
    donante = models.CharField(max_length=200)
    monto = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )

    class Meta:
        ordering = ["-fecha", "donante"]

    def __str__(self):
        return f"{self.donante} - {self.monto}"


class OrdenCompra(models.Model):
    """ Modelo para registrar ordenes de compra de un proyecto """
    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        related_name="ordenes_compra",
    )
    fecha = models.DateField()
    proveedor = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)

    class Meta:
        ordering = ["-fecha", "proveedor"]

    def __str__(self):
        return f"{self.proveedor} - {self.fecha}"

    @property
    def monto_total(self):
        return self.lineas.aggregate(total=Sum("monto"))["total"] or Decimal("0.00")


class LineaOrdenCompra(models.Model):
    """ Modelo para detallar los rubros y montos de una orden de compra """
    orden_compra = models.ForeignKey(
        OrdenCompra,
        on_delete=models.CASCADE,
        related_name="lineas",
    )
    presupuesto = models.ForeignKey(
        Presupuesto,
        on_delete=models.CASCADE,
        related_name="lineas_orden_compra",
    )
    monto = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )

    class Meta:
        ordering = ["presupuesto__rubro"]
        constraints = [
            models.UniqueConstraint(
                fields=["orden_compra", "presupuesto"],
                name="unique_presupuesto_por_orden_compra",
            )
        ]

    def __str__(self):
        return f"{self.presupuesto.rubro} - {self.monto}"
