from model_bakery.baker import make

from apps.address_registry.models import (
    Administration,
    Continent,
    Country,
    County,
    Document,
    DocumentAuthor,
    Eldership,
    Municipality,
    Settlement,
    Title,
)


class TestCountry:
    def test_to_dict(self) -> None:
        country = make(Country)
        assert country.to_dict() == {
            "id": country.id,
            "code": country.code,
            "title_lt": country.title_lt,
            "title_en": country.title_en,
            "continent_id": country.continent_id,
            "title": country.title,
        }

    def test_generate_test_data(self) -> None:
        Country.generate_test_data(quantity=2)
        assert Country.objects.count() == 2


class TestAdministration:
    def test_to_dict(self) -> None:
        administration = make(Administration)
        assert administration.to_dict() == {
            "id": administration.id,
            "country_id": administration.country_id,
        }


class TestTitle:
    def test_to_dict(self) -> None:
        title = make(Title)
        assert title.to_dict() == {
            "id": title.id,
            "title": title.title,
            "accented": title.accented,
            "grammatical_case": title.grammatical_case,
            "settlement_id": title.settlement_id,
        }

    def test_generate_test_data(self) -> None:
        Title.generate_test_data(quantity=2)
        assert Title.objects.count() == 2


class TestContinent:
    def test_to_dict(self) -> None:
        continent = make(Continent)
        assert continent.to_dict() == {
            "code": continent.code,
            "name": continent.name,
        }

    def test_generate_test_data(self) -> None:
        # TODO check if code is necessary to be primary
        Continent.generate_test_data(quantity=2)
        assert Continent.objects.count() == 2


class TestSettlement:
    def test_to_dict(self) -> None:
        settlement = make(Settlement)
        assert settlement.to_dict() == {
            "id": settlement.id,
            "registered": settlement.registered,
            "deregistered": settlement.deregistered,
            "title_lt": settlement.title_lt,
            "area": settlement.area,
            "type": settlement.type,
            "country_id": settlement.country_id,
            "country_code": settlement.country_code,
        }

    def test_generate_test_data(self) -> None:
        Settlement.generate_test_data(quantity=2)
        assert Settlement.objects.count() == 2
        assert Title.objects.count() == 2
        assert Country.objects.count() == 2


class TestDocument:
    def test_to_dict(self) -> None:
        document = make(Document)
        assert document.to_dict() == {
            "id": document.id,
            "number": document.number,
            "type": document.type,
            "content": document.content,
            "status": document.status,
            "received": document.received,
            "creation_date": document.creation_date,
            "creation_time": document.creation_time,
        }

    def test_generate_test_data(self) -> None:
        Document.generate_test_data(quantity=2)
        assert Document.objects.count() == 2
        assert DocumentAuthor.objects.count() == 2


class TestDocumentAuthor:
    def test_to_dict(self) -> None:
        document_author = make(DocumentAuthor)
        assert document_author.to_dict() == {
            "id": document_author.id,
            "document_id": document_author.document_id,
            "name": document_author.name,
            "surname": document_author.surname,
            "passport": document_author.passport,
        }


class TestCounty:
    def test_to_dict(self) -> None:
        county = make(County)
        assert county.to_dict() == {
            "id": county.id,
            "uuid": county.uuid,
            "code": county.code,
            "registered": county.registered,
            "deregistered": county.deregistered,
            "title": county.title,
            "area": county.area,
            "type": county.type,
            "centre_id": county.centre_id,
            "country_id": county.country_id,
            "country_code": county.country_code,
        }

    def test_generate_test_data(self) -> None:
        County.generate_test_data(quantity=2)
        assert County.objects.count() == 2


class TestMunicipality:
    def test_to_dict(self) -> None:
        municipality = make(Municipality)
        assert municipality.to_dict() == {
            "id": municipality.id,
            "uuid": municipality.uuid,
            "code": municipality.code,
            "registered": municipality.registered,
            "deregistered": municipality.deregistered,
            "title": municipality.title,
            "area": municipality.area,
            "type": municipality.type,
            "centre_id": municipality.centre_id,
            "country_id": municipality.country_id,
            "country_code": municipality.country_code,
            "county_id": municipality.county_id,
        }

    def test_generate_test_data(self) -> None:
        Municipality.generate_test_data(quantity=2)
        assert Municipality.objects.count() == 2
        assert County.objects.count() == 2
        assert Settlement.objects.count() == 2


class TestEldership:
    def test_to_dict(self) -> None:
        eldership = make(Eldership)
        assert eldership.to_dict() == {
            "id": eldership.id,
            "uuid": eldership.uuid,
            "code": eldership.code,
            "registered": eldership.registered,
            "deregistered": eldership.deregistered,
            "title": eldership.title,
            "area": eldership.area,
            "type": eldership.type,
            "centre_id": eldership.centre_id,
            "country_id": eldership.country_id,
            "country_code": eldership.country_code,
            "municipality_id": eldership.municipality_id,
        }

    def test_generate_test_data(self) -> None:
        Eldership.generate_test_data(quantity=2)
        assert Eldership.objects.count() == 2
        assert Municipality.objects.count() == 2
        assert Settlement.objects.count() == 2
