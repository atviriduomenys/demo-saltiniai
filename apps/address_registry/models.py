import random
from uuid import uuid4

from django.db import models
from model_bakery.baker import make_recipe

SETTLEMENT_TYPE = ["SMALL TOWN", "HAMLET", "VILLAGE"]
GRAMMATICAL_CASE = ["NOMINATIVE", "GENITIVE"]
ADMINISTRATIVE_UNIT_TYPE = ["MUNICIPALITY", "COUNTY", "ELDERSHIP"]
DOCUMENT_TYPE = ["ORDER", "LETTER"]
DOCUMENT_STATUS = ["REGISTERED", "AMENDMENT", "DEREGISTERED"]


def get_settlement_type() -> dict[str, str]:
    return {i: i for i in SETTLEMENT_TYPE}


def get_grammatical_case() -> dict[str, str]:
    return {i: i for i in GRAMMATICAL_CASE}


def get_administrative_unit_type() -> dict[str, str]:
    return {i: i for i in ADMINISTRATIVE_UNIT_TYPE}


def get_doc_type() -> dict[str, str]:
    return {i: i for i in DOCUMENT_TYPE}


def get_doc_status() -> dict[str, str]:
    return {i: i for i in DOCUMENT_STATUS}


class GenerateTestDataMixin:
    @classmethod
    def generate_test_data(cls, quantity: int = 1, **kwargs):
        raise NotImplementedError("generate_test_data method is not implemented")


class Continent(models.Model):
    code = models.IntegerField(primary_key=True, unique=True)
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Continent"
        verbose_name_plural = "Continents"

    def __str__(self) -> str:
        return self.name

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "name": self.name,
        }

    @classmethod
    def generate_test_data(cls, quantity: int = 1, **kwargs) -> list["Continent"]:
        return make_recipe(
            "address_registry.continent",
            _fill_optional=True,
            _quantity=quantity,
        )


class Document(models.Model):
    number = models.CharField(max_length=255)
    received = models.DateField()
    content = models.BinaryField()
    status = models.CharField(choices=get_doc_status, max_length=255)  # type: ignore
    type = models.CharField(choices=get_doc_type, max_length=255)  # type: ignore
    creation_date = models.DateField()
    creation_time = models.TimeField()

    class Meta:
        verbose_name = "Document"
        verbose_name_plural = "Documents"

    def __str__(self) -> str:
        return self.number

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "number": self.number,
            "received": self.received,
            "content": self.content,
            "status": self.status,
            "type": self.type,
            "creation_date": self.creation_date,
            "creation_time": self.creation_time,
        }

    # TODO: Add test data generators
    @classmethod
    def generate_test_data(cls, quantity: int = 1, **kwargs) -> list["Document"]:
        return make_recipe(
            "address_registry.document_author",
            _fill_optional=True,
            _quantity=quantity,
        )


class DocumentAuthor(models.Model):
    name = models.CharField(max_length=255)
    surname = models.CharField(max_length=255)
    passport = models.FileField(upload_to="passport", null=True)
    document = models.OneToOneField(Document, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = "Document Author"
        verbose_name_plural = "Document Authors"

    def __str__(self) -> str:
        return f"Autorius: {self.name} {self.surname}"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "surname": self.surname,
            "passport": self.passport.name if self.passport else None,
            "document_id": getattr(self, "document_id", None),
        }


class Country(models.Model):
    code = models.CharField(max_length=50)
    title = models.CharField(max_length=255)
    title_lt = models.CharField(max_length=255)
    title_en = models.CharField(max_length=255)
    continent = models.ForeignKey(Continent, on_delete=models.CASCADE)  # type: ignore

    class Meta:
        verbose_name = "Country"
        verbose_name_plural = "Countries"

    def __str__(self) -> str:
        return self.code

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "code": self.code,
            "title": self.title,
            "title_lt": self.title_lt,
            "title_en": self.title_en,
            "continent_id": self.continent_id,
        }

    @classmethod
    def generate_test_data(cls, quantity: int = 1, **kwargs) -> list["Country"]:
        countries = []
        for _ in range(quantity):
            continent = kwargs.get("continent") or Continent.generate_test_data()[0]

            country = make_recipe(
                "address_registry.country",
                code=random.random(),
                continent=continent,
                _fill_optional=True,
            )

            countries.append(country)

        return countries


class Settlement(models.Model):
    registered = models.DateField(null=True)
    deregistered = models.DateField(null=True)
    title_lt = models.CharField(max_length=255)
    area = models.FloatField(null=True)
    type = models.CharField(choices=get_settlement_type, max_length=255)  # type: ignore
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    country_code = models.CharField(max_length=50, help_text="Must match with country_id")

    class Meta:
        verbose_name = "Settlement"
        verbose_name_plural = "Settlements"

    def __str__(self) -> str:
        return self.title_lt

    def save(self, *args, **kwargs) -> None:
        self.country_code = self.country.code

        update_fields = kwargs.get("update_fields")
        if update_fields is not None and "country" in update_fields:
            kwargs["update_fields"] = {"country_code"}.union(update_fields)
        return super().save(*args, **kwargs)

    def to_dict(self):
        return {
            "id": self.id,
            "registered": self.registered,
            "deregistered": self.deregistered,
            "title_lt": self.title_lt,
            "area": self.area,
            "type": self.type,
            "country_id": self.country_id,
            "country_code": self.country_code,
        }

    @classmethod
    def generate_test_data(cls, quantity: int = 1, **kwargs) -> list["Settlement"]:
        settlements = []
        for _ in range(quantity):
            country = kwargs.get("country") or Country.generate_test_data()[0]

            settlement = make_recipe(
                "address_registry.settlement",
                country=country,
                _fill_optional=True,
            )

            make_recipe("address_registry.title", _fill_optional=True, settlement=settlement)

            settlements.append(settlement)

        return settlements


class Title(models.Model):
    title = models.CharField(max_length=255)
    accented = models.CharField(max_length=255)
    grammatical_case = models.CharField(choices=get_grammatical_case, max_length=255)  # type: ignore
    settlement = models.ForeignKey(Settlement, on_delete=models.SET_NULL, related_name="title_forms", null=True)

    class Meta:
        verbose_name = "Title"
        verbose_name_plural = "Titles"

    def __str__(self) -> str:
        return self.title

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "accented": self.accented,
            "grammatical_case": self.grammatical_case,
            "settlement_id": getattr(self, "settlement_id", None),
        }

    @classmethod
    def generate_test_data(cls, quantity: int = 1, **kwargs) -> list["Title"]:
        return make_recipe("address_registry.title", _fill_optional=True, _quantity=quantity)


class AdministrativeUnit(models.Model):
    uuid = models.UUIDField(unique=True, editable=False, default=uuid4)
    code = models.FloatField(null=True)
    registered = models.DateField(null=True)
    deregistered = models.DateField(null=True)
    title = models.CharField(max_length=255)
    area = models.FloatField(null=True)
    type = models.CharField(choices=get_administrative_unit_type, max_length=255)  # type: ignore
    centre = models.ForeignKey(Settlement, on_delete=models.CASCADE)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    country_code = models.CharField(max_length=50, help_text="Must match with country_id")

    class Meta:
        verbose_name = "Administrative Unit"
        verbose_name_plural = "Administrative Units"

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs) -> None:
        self.country_code = self.country.code

        update_fields = kwargs.get("update_fields")
        if update_fields is not None and "country" in update_fields:
            kwargs["update_fields"] = {"country_code"}.union(update_fields)
        return super().save(*args, **kwargs)

    def to_dict(self) -> dict:
        return {
            "uuid": self.uuid,
            "country_code": self.country_code,
            "code": self.code,
            "registered": self.registered,
            "deregistered": self.deregistered,
            "title": self.title,
            "area": self.area,
            "type": self.type,
            "centre_id": getattr(self, "centre_id", None),
            "country_id": getattr(self, "country_id", None),
        }

    @classmethod
    def generate_test_data(cls, quantity: int = 1, **kwargs) -> list["AdministrativeUnit"]:
        administrative_units = []
        for _ in range(quantity):
            settlement = kwargs.get("settlement") or Settlement.generate_test_data()[0]
            administrative_unit = make_recipe(
                "address_registry.administrative_unit",
                type=kwargs.get("type", random.choice(ADMINISTRATIVE_UNIT_TYPE)),
                country=settlement.country,
                centre=settlement,
                _fill_optional=True,
            )
            administrative_units.append(administrative_unit)

        return administrative_units


class Administration(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    admin_unit = models.ForeignKey(AdministrativeUnit, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Administration"
        verbose_name_plural = "Administrations"

    def __str__(self) -> str:
        return f"{self.country}"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "country": self.country,
        }

    @classmethod
    def generate_test_data(cls, quantity: int = 1, **kwargs) -> list["Administration"]:
        administrations = []
        for _ in range(quantity):
            admin_unit = kwargs.get("Administration") or AdministrativeUnit.generate_test_data(quantity=1)[0]
            administration = make_recipe(
                "address_registry.administration",
                admin_unit=admin_unit,
                country=admin_unit.country,
                _fill_optional=True,
            )

            administrations.append(administration)

        return administrations


class County(models.Model):
    admin_unit = models.ForeignKey(AdministrativeUnit, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "County"
        verbose_name_plural = "Counties"

    def __str__(self) -> str:
        return str(self.id)

    def to_dict(self) -> dict:
        return {"id": self.id, **self.admin_unit.to_dict()}

    @classmethod
    def generate_test_data(cls, quantity: int = 1, **kwargs) -> list["AdministrativeUnit"]:
        counties = []
        for _ in range(quantity):
            admin_unit = AdministrativeUnit.generate_test_data(quantity=1, type="COUNTY")[0]

            county = make_recipe(
                "address_registry.county",
                admin_unit=admin_unit,
                _fill_optional=True,
            )

            counties.append(county)
        return counties


class Municipality(models.Model):
    county = models.ForeignKey(County, on_delete=models.SET_NULL, null=True)
    admin_unit = models.ForeignKey(AdministrativeUnit, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Municipality"
        verbose_name_plural = "Municipalities"

    def __str__(self) -> str:
        return str(self.id)

    def to_dict(self) -> dict:
        return {"id": self.id, "county_id": self.county_id, **self.admin_unit.to_dict()}

    @classmethod
    def generate_test_data(cls, quantity: int = 1, **kwargs) -> list["AdministrativeUnit"]:
        municipalities = []
        for _ in range(quantity):
            county = County.generate_test_data(quantity=1)[0]
            admin_unit = AdministrativeUnit.generate_test_data(quantity=1, type="MUNICIPALITY")[0]

            municipality = make_recipe(
                "address_registry.municipality",
                county=county,
                admin_unit=admin_unit,
                _fill_optional=True,
            )

            municipalities.append(municipality)
        return municipalities


class Eldership(models.Model):
    municipality = models.ForeignKey(Municipality, on_delete=models.SET_NULL, null=True)
    admin_unit = models.ForeignKey(AdministrativeUnit, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Eldership"
        verbose_name_plural = "Elderships"

    def __str__(self) -> str:
        return str(self.id)

    def to_dict(self) -> dict:
        return {"id": self.id, "municipality_id": self.municipality_id, **self.admin_unit.to_dict()}

    @classmethod
    def generate_test_data(cls, quantity: int = 1, **kwargs) -> list["AdministrativeUnit"]:
        elderships = []
        for _ in range(quantity):
            admin_unit = AdministrativeUnit.generate_test_data(quantity=1, type="ELDERSHIP")[0]

            municipality = Municipality.generate_test_data(quantity=1)[0]

            eldership = make_recipe(
                "address_registry.eldership",
                municipality=municipality,
                admin_unit=admin_unit,
                _fill_optional=True,
            )

            elderships.append(eldership)
        return elderships
