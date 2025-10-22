import xml.etree.ElementTree as ET

from apps.address_registry.models import Country


def construct_country_xml(country: Country) -> ET.Element:
    country_data = ET.Element("countryData")
    ET.SubElement(country_data, "id").text = str(country.id)
    ET.SubElement(country_data, "title").text = country.title
    ET.SubElement(country_data, "continent_id").text = str(country.continent_id)

    continent_data = ET.SubElement(country_data, "continent")
    ET.SubElement(continent_data, "code").text = str(country.continent.code)
    ET.SubElement(continent_data, "name").text = country.continent.name

    return country_data


def construct_countries_xml() -> ET.Element:
    countries = ET.Element("countries")
    for country in Country.objects.all().select_related("continent"):
        countries.append(construct_country_xml(country))

    return countries
