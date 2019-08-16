import requests
import xmltodict
from party.models import Party
from politician.models import Politician


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


class PoliticianService:

    def __init__(self):
        self._party_service = PartyService()
        self._parties_by_initials = {}

    def get_by_external_id(self, external_id, role):
        return Politician.objects \
            .filter(external_id=external_id, role=role) \
            .first()

    def _get_party_by_initial(self, initials):
        if initials in self._parties_by_initials:
            return self._parties_by_initials[initials]

        party = self._party_service.get_by_initials(initials)
        if not party:
            return None

        self._parties_by_initials[initials] = party
        return self._get_party_by_initial(initials)


class SenateService(PoliticianService):

    def __init__(self):
        super(SenateService, self).__init__()

        self._host = "http://legis.senado.leg.br"

    def load_politicians(self):
        response = requests.get(
            "{}/dadosabertos/senador/lista/atual".format(self._host))
        result = xmltodict.parse(response.content.decode())

        politicians = result["ListaParlamentarEmExercicio"]["Parlamentares"]
        for data in politicians["Parlamentar"]:
            identity = data["IdentificacaoParlamentar"]

            politician = self.get_by_external_id(
                identity["CodigoParlamentar"],
                Politician.SENATOR)
            if not politician:
                politician = Politician(role=Politician.SENATOR)

            politician.picture = identity["UrlFotoParlamentar"]
            politician.name = identity["NomeCompletoParlamentar"]
            politician.external_id = identity["CodigoParlamentar"]
            politician.party = self._get_party_by_initial(
                identity["SiglaPartidoParlamentar"])

            politician.save()


class CongressService(PoliticianService):

    def __init__(self):
        super(CongressService, self).__init__()

        self._host = "https://dadosabertos.camara.leg.br"

    def load_politicians(self):
        response = requests.get(
            "{}/api/v2/deputados".format(self._host),
            params={
                "itens": 1000
            })
        result = response.json()

        for data in result["dados"]:
            politician = self.get_by_external_id(data["id"], Politician.DEPUTY)
            if not politician:
                politician = Politician(role=Politician.DEPUTY)

            politician.picture = data["urlFoto"]
            politician.name = self._capitalize_name(data["nome"])
            politician.external_id = data["id"]
            politician.party = self._get_party_by_initial(data["siglaPartido"])

            politician.save()

    def _capitalize_name(self, name):
        return " ".join([n.capitalize() for n in name.split(" ")])
