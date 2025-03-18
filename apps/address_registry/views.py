from django.views.decorators.csrf import csrf_exempt
from spyne.application import Application
from spyne.protocol.http import HttpRpc
from spyne.protocol.json import JsonDocument
from spyne.protocol.soap import Soap11
from spyne.protocol.xml import XmlDocument
from spyne.server.django import DjangoApplication

from apps.address_registry.services import DemoService

demo_application_json = csrf_exempt(
    DjangoApplication(
        Application(
            [DemoService],
            tns="demo_service_json",
            name="Demo JSON Service",
            in_protocol=HttpRpc(validator="soft"),
            out_protocol=JsonDocument(validator="soft"),
        )
    )
)


demo_application_soap = csrf_exempt(
    DjangoApplication(
        Application(
            [DemoService],
            tns="demo_service_soap",
            name="Demo SOAP Service",
            in_protocol=HttpRpc(validator="soft"),
            out_protocol=Soap11(validator="soft"),
        )
    )
)


demo_application_xml = csrf_exempt(
    DjangoApplication(
        Application(
            [DemoService],
            tns="demo_service_xml",
            name="Demo XML Service",
            in_protocol=HttpRpc(validator="soft"),
            out_protocol=XmlDocument(validator="soft"),
        )
    )
)
