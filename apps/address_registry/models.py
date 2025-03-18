from django.db import models

VIETOVES_TIPAI = ["MIESTAS", "MIESTELIS", "KAIMAS", "VIENSEDIS"]
LINKSNIAI = ["VARDININKAS", "KILMININKAS"]


def get_vietoves_tipai() -> dict[str, str]:
    return {i: i for i in VIETOVES_TIPAI}


def get_linksniai() -> dict[str, str]:
    return {i: i for i in LINKSNIAI}


class Gyvenviete(models.Model):
    isregistruota = models.DateField()
    registruota = models.DateField()
    pavadinimas = models.CharField(max_length=255)
    kurortas = models.BooleanField()
    plotas = models.FloatField()
    tipas = models.CharField(choices=get_vietoves_tipai)  # type: ignore

    class Meta:
        verbose_name = "Gyvenviete"
        verbose_name_plural = "Gyvenvietes"

    def __str__(self) -> str:
        return self.pavadinimas


class Pavadinimas(models.Model):
    pavadinimas = models.CharField(max_length=255)
    kirciuotas = models.CharField(max_length=255)
    linksnis = models.CharField(choices=get_linksniai, max_length=255)  # type: ignore
    gyvenviete = models.ForeignKey(
        Gyvenviete,
        related_name="pavadinimo_formos",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Pavadinimas"
        verbose_name_plural = "Pavadinimai"

    def __str__(self) -> str:
        return self.pavadinimas
