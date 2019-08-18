import requests
import xmltodict
from party.models import Party
from party.services import PartyService
from politician.models import Politician
from politisys.services import BaseQueryService


class PoliticianService(BaseQueryService):
    model = Politician
    select_related = ["party"]

    def __init__(self):
        super(BaseQueryService, self).__init__()

        self._party_service = PartyService()
        self._parties_by_initials = {}

    def get_by_external_id(self, external_id, role):
        return Politician.objects \
            .filter(external_id=external_id, role=role) \
            .first()

    def additional_queryset(self, queryset, params):
        if "search" in params and params["search"]:
            queryset = queryset.filter(name__icontains=params["search"])

        return queryset.filter(active=True)

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

    def get_last_law_projects(self, politician):
        response = requests.get("{}/dadosabertos/senador/{}/autorias".format(
            self._host,
            politician.external_id), headers={
                "Accept": "application/json"
        })
        data = response.json()

        return [{
            "id": news["Materia"]["IdentificacaoMateria"]["CodigoMateria"],
            "code": news["Materia"]["IdentificacaoMateria"]["DescricaoIdentificacaoMateria"],
            "description": news["Materia"]["EmentaMateria"] if "EmentaMateria" in news["Materia"] else None,
        } for news in data["MateriasAutoriaParlamentar"]["Parlamentar"]["Autorias"]["Autoria"]]

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
            politician.role_state = identity["UfParlamentar"]

            politician.save()


class CongressService(PoliticianService):

    def __init__(self):
        super(CongressService, self).__init__()

        self._host = "https://dadosabertos.camara.leg.br"

    def get_last_law_projects(self, politician):
        response = requests.get(
            "{}/api/v2/proposicoes".format(self._host),
            params={
                "idDeputadoAutor": politician.external_id,
                "itens": 1000
            }, headers={
                "Accept": "application/json"
            })
        data = response.json()

        return [{
            "id": law["id"],
            "code": "{} {}/{}".format(
                law["siglaTipo"],
                law["numero"],
                law["ano"]),
            "description": law["ementa"]
        } for law in data["dados"]]

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
            politician.role_state = data["siglaUf"]

            politician.save()

    def _capitalize_name(self, name):
        return " ".join([n.capitalize() for n in name.split(" ")])
