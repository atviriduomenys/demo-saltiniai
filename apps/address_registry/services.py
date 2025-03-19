from django.db.models import QuerySet
from spyne import Iterable, String, rpc
from spyne.service import Service

from apps.address_registry.models import Gyvenviete, Pavadinimas
from apps.address_registry.schema import GyvenvieteBaseModel, GyvenvieteNestedModel, PavadinimaiBaseModel


class DemoService(Service):
    @rpc(String, _returns=Iterable(GyvenvieteBaseModel))
    def gyvenviete(self, pavadinimas: str | None) -> QuerySet:
        queryset = Gyvenviete.objects.all()
        if pavadinimas:
            queryset = queryset.filter(pavadinimas__icontains=pavadinimas)
        return queryset

    @rpc(String, _returns=Iterable(PavadinimaiBaseModel))
    def pavadinimas(self, pavadinimas: str | None) -> QuerySet:
        queryset = Pavadinimas.objects.all()
        if pavadinimas:
            queryset = queryset.filter(pavadinimas__icontains=pavadinimas)
        return queryset

    @rpc(String, _returns=Iterable(GyvenvieteNestedModel))
    def gyvenviete_pavadinimai(self, pavadinimas: str | None) -> list:
        gyvenviete_queryset = Gyvenviete.objects.all().prefetch_related("pavadinimo_formos")
        if pavadinimas:
            gyvenviete_queryset = gyvenviete_queryset.filter(pavadinimas__icontains=pavadinimas)

        return [
            {
                "id": g.id,
                "isregistruota": g.isregistruota,
                "registruota": g.registruota,
                "pavadinimas": g.pavadinimas,
                "kurortas": g.kurortas,
                "plotas": g.plotas,
                "tipas": g.tipas,
                "pavadinimo_formos": [
                    {
                        "pavadinimas": p.pavadinimas,
                        "kirciuotas": p.kirciuotas,
                        "linksnis": p.linksnis,
                        "gyvenviete_id": p.gyvenviete_id,
                    }
                    for p in g.pavadinimo_formos.all()
                ],
            }
            for g in gyvenviete_queryset
        ]
