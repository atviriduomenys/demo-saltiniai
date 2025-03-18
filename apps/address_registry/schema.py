from spyne import Array, Boolean, ComplexModel, Date, Float, Integer, String

# Spyne calls it models. Basically defines response schemas


class GyvenvieteBaseModel(ComplexModel):
    id = Integer()
    isregistruota = Date()
    registruota = Date()
    pavadinimas = String()
    kurortas = Boolean()
    plotas = Float()
    tipas = String()


class PavadinimaiBaseModel(ComplexModel):
    pavadinimas = String()
    kirciuotas = String()
    linksnis = String()
    gyvenviete_id = Integer()


class GyvenvieteNestedModel(GyvenvieteBaseModel):
    pavadinimo_formos = Array(PavadinimaiBaseModel)
