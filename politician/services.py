import requests
import xmltodict
from politician.models import Party, Politician


class PartyService:

    def __init__(self):
        self._host = "https://dadosabertos.camara.leg.br"

    def load_parties(self):
        response = requests.get(
            "{}/api/v2/partidos?itens=1000".format(self._host))
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


class SenateService:

    def __init__(self):
        self._host = "http://legis.senado.leg.br"

        self._party_service = PartyService()
        self._parties_by_initials = {}

    def get_by_external_id(self, external_id):
        return Politician.objects \
            .filter(external_id=external_id) \
            .first()

    def load_politicians(self):
        response = requests.get(
            "{}/dadosabertos/senador/lista/atual".format(self._host))
        result = xmltodict.parse(response.content.decode())

        politicians = result["ListaParlamentarEmExercicio"]["Parlamentares"]
        for data in politicians["Parlamentar"]:
            identity = data["IdentificacaoParlamentar"]

            politician = self.get_by_external_id(identity["CodigoParlamentar"])
            if not politician:
                politician = Politician()

            politician.picture = identity["UrlFotoParlamentar"]
            politician.name = identity["NomeCompletoParlamentar"]
            politician.role = Politician.SENATOR
            politician.external_id = identity["CodigoParlamentar"]
            politician.party = self._get_party_by_initial(
                identity["SiglaPartidoParlamentar"])

            politician.save()

    def _get_party_by_initial(self, initials):
        if initials in self._parties_by_initials:
            return self._parties_by_initials[initials]

        party = self._party_service.get_by_initials(initials)
        if not party:
            return None

        self._parties_by_initials[initials] = party
        return self._get_party_by_initial(initials)
