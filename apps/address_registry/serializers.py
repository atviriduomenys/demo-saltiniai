from rest_framework import serializers

from apps.address_registry.models import (
    Continent,
    Country,
    Document,
    DocumentAuthor,
    Settlement,
    Title,
)


class ContinentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Continent
        fields = "__all__"


class TitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Title
        fields = "__all__"


class SettlementSerializer(serializers.ModelSerializer):
    title_forms = TitleSerializer(many=True)

    class Meta:
        model = Settlement
        fields = "__all__"


class CountrySerializer(serializers.ModelSerializer):
    continent = ContinentSerializer(many=True, read_only=True)

    class Meta:
        model = Country
        fields = "__all__"


class DocumentAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentAuthor
        fields = "__all__"


class DocumentSerializer(serializers.ModelSerializer):
    document_author = DocumentAuthorSerializer(source="documentauthor", read_only=True)

    class Meta:
        model = Document
        fields = "__all__"


class CountrySettlementSerializer(serializers.ModelSerializer):
    settlements = SettlementSerializer(many=True, read_only=True)

    class Meta:
        model = Country
        fields = [field.name for field in Country._meta.fields] + ["settlements"]


class ContinentCountrySettlementSerializer(serializers.ModelSerializer):
    countries = CountrySettlementSerializer(many=True, read_only=True)

    class Meta:
        model = Continent
        fields = ["code", "name", "countries"]
