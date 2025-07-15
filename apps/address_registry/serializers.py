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
    continent = ContinentSerializer(read_only=True)

    class Meta:
        model = Country
        fields = "__all__"


class ContinentCountrySerializer(serializers.ModelSerializer):
    countries = CountrySerializer(many=True, read_only=True)

    class Meta:
        model = Continent
        fields = [field.name for field in Continent._meta.fields] + ["countries"]


class DocumentAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentAuthor
        fields = "__all__"


class DocumentSerializer(serializers.ModelSerializer):
    document_author = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = "__all__"

    def get_document_author(self, obj):
        author = getattr(obj, "documentauthor", None)
        if author:
            return [DocumentAuthorSerializer(author).data]
        return []


class CountrySettlementSerializer(serializers.ModelSerializer):
    settlements = SettlementSerializer(many=True, read_only=True)

    class Meta:
        model = Country
        fields = [field.name for field in Country._meta.fields] + ["settlements"]


class ContinentCountrySettlementSerializer(serializers.ModelSerializer):
    countries = CountrySettlementSerializer(many=True, read_only=True)
    continent = ContinentSerializer(read_only=True)

    class Meta:
        model = Continent
        fields = [field.name for field in Continent._meta.fields] + ["countries"] + ["continent"]
