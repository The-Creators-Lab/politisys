import requests
from party.models import Party


class PartyService:

    def __init__(self):
        self._host = "https://dadosabertos.camara.leg.br"

    def load_parties(self):
        response = requests.get(
            "{}/api/v2/partidos".format(self._host),
            params={
                "itens": 1000
            })
        result = response.json()

        for data in result["dados"]:
            party = self.get_by_external_id(data["id"])
            if not party:
                party = Party()

            party.name = data["nome"]
            party.initials = data["sigla"]
            party.external_id = data["id"]
            party.save()

    def get_by_initials(self, initial):
        return Party.objects.filter(initials=initial).first()

    def get_by_external_id(self, external_id):
        return Party.objects \
            .filter(external_id=external_id) \
            .first()
