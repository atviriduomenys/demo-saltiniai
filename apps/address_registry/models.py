from uuid import uuid4

from django.contrib.gis.db import models as gis_models
from django.db import models
from model_bakery.baker import make_recipe

VIETOVES_TIPAI = ["MIESTAS", "MIESTELIS", "KAIMAS", "VIENSEDIS"]
LINKSNIAI = ["VARDININKAS", "KILMININKAS", "NAUDININKAS", "GALININKAS", "ĮNAGININKAS", "VIETININKAS", "ŠAUKSMININKAS"]
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


class GenerateTestDataMixin:
    @classmethod
    def generate_test_data(cls, quantity: int = 1, **kwargs):
        raise NotImplementedError("generate_test_data method is not implemented")


class Salis(GenerateTestDataMixin, models.Model):
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

    @classmethod
    def generate_test_data(cls, quantity: int = 1, **kwargs) -> list["Salis"]:
        return make_recipe("address_registry.salis", _fill_optional=True, _quantity=quantity)


class Gyvenviete(GenerateTestDataMixin, models.Model):
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

    @classmethod
    def generate_test_data(cls, quantity: int = 1, **kwargs) -> list["Gyvenviete"]:
        gyvenvietes = []
        for _ in range(quantity):
            salis = kwargs.get("salis") or Salis.generate_test_data()[0]
            gyvenviete = make_recipe("address_registry.gyvenviete", salis=salis, _fill_optional=True)
            make_recipe(
                "address_registry.pavadinimas",
                linksnis="VARDININKAS",
                gyvenviete=gyvenviete,
                _fill_optional=True,
            )
            make_recipe(
                "address_registry.pavadinimas",
                linksnis="KILMININKAS",
                gyvenviete=gyvenviete,
                _fill_optional=True,
            )
            gyvenvietes.append(gyvenviete)

        return gyvenvietes


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


class Dokumentas(GenerateTestDataMixin, models.Model):
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

    @classmethod
    def generate_test_data(cls, quantity: int = 1, **kwargs) -> list["Dokumentas"]:
        return make_recipe(
            "address_registry.dokumento_autorius",
            _fill_optional=True,
            _quantity=quantity,
        )


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


class AdministracinisVienetas(GenerateTestDataMixin, models.Model):
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
    ribos = gis_models.PolygonField(blank=True, null=True)

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
            "ribos": str(self.ribos) if self.ribos else None,
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

    @classmethod
    def generate_test_data(cls, quantity: int = 1, **kwargs) -> list["Apskritis"]:
        apskritys = []
        for _ in range(quantity):
            gyvenviete = Gyvenviete.generate_test_data()[0]
            apskritys.append(
                make_recipe(
                    "address_registry.apskritis",
                    centras=gyvenviete,
                    salis=gyvenviete.salis,
                    _fill_optional=True,
                )
            )

        return apskritys


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

    @classmethod
    def generate_test_data(cls, quantity: int = 1, **kwargs) -> list["Savivaldybe"]:
        savivaldybes = []
        for _ in range(quantity):
            apskritis = Apskritis.generate_test_data()[0]
            gyvenviete = Gyvenviete.generate_test_data(salis=apskritis.salis)[0]

            savivaldybes.append(
                make_recipe(
                    "address_registry.savivaldybe",
                    apskritis=apskritis,
                    centras=gyvenviete,
                    salis=gyvenviete.salis,
                    _fill_optional=True,
                )
            )

        return savivaldybes


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

    @classmethod
    def generate_test_data(cls, quantity: int = 1, **kwargs) -> list["Seniunija"]:
        seniunijos = []
        for _ in range(quantity):
            savivaldybe = Savivaldybe.generate_test_data()[0]
            gyvenviete = Gyvenviete.generate_test_data(salis=savivaldybe.salis)[0]

            seniunijos.append(
                make_recipe(
                    "address_registry.seniunija",
                    savivaldybe=savivaldybe,
                    centras=gyvenviete,
                    salis=gyvenviete.salis,
                    _fill_optional=True,
                )
            )

        return seniunijos


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


class JuridinisAsmuo(GenerateTestDataMixin, Organizacija):
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

    @classmethod
    def generate_test_data(cls, quantity: int = 1, **kwargs) -> list["JuridinisAsmuo"]:
        return make_recipe("address_registry.juridinis_asmuo", _fill_optional=True, _quantity=quantity)


class NejuridinisAsmuo(GenerateTestDataMixin, Organizacija):
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

    @classmethod
    def generate_test_data(cls, quantity: int = 1, **kwargs) -> list["NejuridinisAsmuo"]:
        return make_recipe("address_registry.nejuridinis_asmuo", _fill_optional=True, _quantity=quantity)
