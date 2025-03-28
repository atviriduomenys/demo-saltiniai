from uuid import uuid4

from django.db import models

VIETOVES_TIPAI = ["MIESTAS", "MIESTELIS", "KAIMAS", "VIENSEDIS"]
LINKSNIAI = ["VARDININKAS", "KILMININKAS"]
ADMINISTRACINIO_VIENETO_TIPAI = ["APSKRITIS", "SAVIVALDYBE", "SENIUNIJA"]
DOKUMENTO_RUSIS = ["ISAKYMAS", "RASTAS"]
DOKUMENTO_POZYMIS = ["IREGISTRUOTA", "KEITIMAS", "ISREGISTRUOTA"]


def get_vietoves_tipai() -> dict[str, str]:
    return {i: i for i in VIETOVES_TIPAI}


def get_linksniai() -> dict[str, str]:
    return {i: i for i in LINKSNIAI}


def get_administracinio_vieneto_tipai() -> dict[str, str]:
    return {i: i for i in ADMINISTRACINIO_VIENETO_TIPAI}


def get_dokumento_rusis() -> dict[str, str]:
    return {i: i for i in DOKUMENTO_RUSIS}


def get_dokumento_pozymis() -> dict[str, str]:
    return {i: i for i in DOKUMENTO_POZYMIS}


class Salis(models.Model):
    kodas = models.CharField(max_length=20)
    pavadinimas = models.CharField(max_length=255)
    pavadinimas_lt = models.CharField(max_length=255)
    pavadinimas_en = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Šalis"
        verbose_name_plural = "Šalys"

    def __str__(self):
        return self.pavadinimas_lt

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "kodas": self.kodas,
            "pavadinimas_lt": self.pavadinimas_lt,
            "pavadinimas_en": self.pavadinimas_en,
        }


class Gyvenviete(models.Model):
    isregistruota = models.DateField()
    registruota = models.DateField()
    pavadinimas = models.CharField(max_length=255)
    kurortas = models.BooleanField()
    plotas = models.FloatField()
    tipas = models.CharField(choices=get_vietoves_tipai)  # type: ignore
    salis = models.ForeignKey(Salis, on_delete=models.CASCADE)
    salies_kodas = models.CharField(max_length=20, blank=True, help_text="Turi sutapti su Salis.kodas")

    class Meta:
        verbose_name = "Gyvenviete"
        verbose_name_plural = "Gyvenvietes"

    def __str__(self) -> str:
        return self.pavadinimas

    def save(self, *args, **kwargs) -> None:
        self.salies_kodas = self.salis.kodas

        update_fields = kwargs.get("update_fields")
        if update_fields is not None and "salis" in update_fields:
            kwargs["update_fields"] = {"salies_kodas"}.union(update_fields)
        return super().save(*args, **kwargs)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "isregistruota": self.isregistruota,
            "registruota": self.registruota,
            "pavadinimas": self.pavadinimas,
            "kurortas": self.kurortas,
            "plotas": self.plotas,
            "tipas": self.tipas,
            "salis_id": self.salis.id,
            "salies_kodas": self.salies_kodas,
        }


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
        constraints = [
            models.UniqueConstraint(fields=("gyvenviete", "linksnis"), name="unique_gyvenvietes_linksnis"),
        ]

    def __str__(self) -> str:
        return self.pavadinimas

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "pavadinimas": self.pavadinimas,
            "kirciuotas": self.kirciuotas,
            "linksnis": self.linksnis,
            "gyvenviete": self.gyvenviete_id,
        }


class Dokumentas(models.Model):
    numeris = models.CharField(max_length=255)
    priimta = models.DateField()
    rusis = models.CharField(choices=get_dokumento_rusis, max_length=255)  # type: ignore
    pozymis = models.CharField(choices=get_dokumento_pozymis, max_length=255)  # type: ignore
    sukurimo_data = models.DateField()
    sukurimo_laikas = models.TimeField()

    class Meta:
        verbose_name = "Dokumentas"
        verbose_name_plural = "Dokumentai"

    def __str__(self) -> str:
        return self.numeris

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "numeris": self.numeris,
            "priimta": self.priimta,
            "rusis": self.rusis,
            "pozymis": self.pozymis,
            "sukurimo_data": self.sukurimo_data,
            "sukurimo_laikas": self.sukurimo_laikas,
        }


class DokumentoAutorius(models.Model):
    dokumentas = models.OneToOneField(Dokumentas, null=True, on_delete=models.SET_NULL)
    vardas = models.CharField(max_length=255)
    pavarde = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Dokumento autorius"
        verbose_name_plural = "Dokumento autoriai"

    def __str__(self) -> str:
        return f"Autorius: {self.vardas} {self.pavarde}"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "vardas": self.vardas,
            "pavarde": self.pavarde,
            "dokumentas_id": getattr(self, "dokumentas_id", None),
        }


class AdministracinisVienetas(models.Model):
    uuid = models.UUIDField(unique=True, editable=False, default=uuid4)
    tipas = models.CharField(choices=get_administracinio_vieneto_tipai, max_length=255)  # type: ignore
    kodas = models.IntegerField(unique=True, null=True)
    iregistruota = models.DateTimeField(null=True)
    isregistruota = models.DateTimeField(null=True)
    pavadinimas = models.CharField(max_length=255)
    plotas = models.IntegerField(null=True)
    centras = models.ForeignKey(Gyvenviete, on_delete=models.CASCADE)
    dokumentai = models.ManyToManyField(Dokumentas, blank=True)
    salis = models.ForeignKey(Salis, on_delete=models.CASCADE)
    salies_kodas = models.CharField(max_length=20, blank=True, help_text="Turi sutapti su Salis.kodas")

    class Meta:
        abstract = True

    def save(self, *args, **kwargs) -> None:
        self.salies_kodas = self.salis.kodas

        update_fields = kwargs.get("update_fields")
        if update_fields is not None and "salis" in update_fields:
            kwargs["update_fields"] = {"salies_kodas"}.union(update_fields)
        return super().save(*args, **kwargs)

    def to_dict(self) -> dict:
        return {
            "uuid": self.uuid,
            "tipas": self.tipas,
            "kodas": self.kodas,
            "iregistruota": self.iregistruota,
            "isregistruota": self.isregistruota,
            "pavadinimas": self.pavadinimas,
            "plotas": self.plotas,
            "centras_id": self.centras_id,
            "salis_id": self.salis_id,
            "salies_kodas": self.salies_kodas,
        }


class Apskritis(AdministracinisVienetas):
    class Meta:
        verbose_name = "Apskritis"
        verbose_name_plural = "Apskritys"

    def __str__(self) -> str:
        return self.pavadinimas

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            **super().to_dict(),
        }


class Savivaldybe(AdministracinisVienetas):
    apskritis = models.ForeignKey(Apskritis, on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = "Savivaldybė"
        verbose_name_plural = "Savivaldybės"

    def __str__(self) -> str:
        return self.pavadinimas

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            **super().to_dict(),
            "apskritis_id": self.apskritis_id,
        }


class Seniunija(AdministracinisVienetas):
    savivaldybe = models.ForeignKey(Savivaldybe, on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = "Seniūnija"
        verbose_name_plural = "Seniūnijos"

    def __str__(self) -> str:
        return self.pavadinimas

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            **super().to_dict(),
            "savivaldybe_id": self.savivaldybe_id,
        }


class Organizacija(models.Model):
    class Meta:
        verbose_name = "Organizacija"
        verbose_name_plural = "Organizacijos"

    def __str__(self) -> str:
        return str(self.id)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
        }


class JuridinisAsmuo(Organizacija):
    pavadinimas = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Juridinis asmuo"
        verbose_name_plural = "Juridiniai asmenys"

    def __str__(self) -> str:
        return self.pavadinimas

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "pavadinimas": self.pavadinimas,
        }


class NejuridinisAsmuo(Organizacija):
    pavadinimas = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Nejuridinis asmuo"
        verbose_name_plural = "Nejuridiniai asmenys"

    def __str__(self) -> str:
        return self.pavadinimas

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "pavadinimas": self.pavadinimas,
        }
