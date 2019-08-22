from datetime import datetime
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

        return queryset.filter(active=True).order_by("name")

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

    def get_by_id(self, senator_id):
        response = requests.get(
            "{}/dadosabertos/senador/{}".format(self._host, senator_id),
            headers={
                "Accept": "application/json"
            })
        data = response.json()

        politician = data["DetalheParlamentar"]["Parlamentar"]
        identity = politician["IdentificacaoParlamentar"]
        basic = politician["DadosBasicosParlamentar"]
        return {
            "birthday": datetime.strptime(basic["DataNascimento"], "%Y-%m-%d"),
            "email": identity["EmailParlamentar"],
            "genre": identity["SexoParlamentar"]
        }

    def get_current_year_expenses(self, politician):
        return []

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

    def get_by_id(self, senator_id):
        response = requests.get(
            "{}/api/v2/deputados/{}".format(self._host, senator_id),
            headers={
                "Accept": "application/json"
            })
        data = response.json()

        return {
            "birthday": datetime.strptime(data["dados"]["dataNascimento"], "%Y-%m-%d"),
            "email": data["dados"]["email"],
            "genre": "Masculino" if data["dados"]["sexo"] == "M" else "Feminino"
        }

    def get_current_year_expenses(self, politician):
        response = requests.get(
            "{}/api/v2/deputados/{}/despesas".format(
                self._host, politician.external_id),
            params={
                "itens": 10000,
                "ano": datetime.now().year,
                "ordenarPor": "dataDocumento"
            },
            headers={
                "Accept": "application/json"
            })
        data = response.json()

        return [{
            "document": expense["numDocumento"],
            "code": expense["codDocumento"],
            "type": expense["tipoDespesa"],
            "provider": expense["nomeFornecedor"],
            "price": expense["valorDocumento"],
            "date": datetime.strptime(expense["dataDocumento"], "%Y-%m-%d") if expense["dataDocumento"] else None
        } for expense in data["dados"]]

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

    def get_proposition_by_id(self, proposition_id):
        response = requests.get(
            "{}/api/v2/proposicoes/{}".format(self._host, proposition_id),
            headers={
                "Accept": "application/json"
            })
        data = response.json()

        law = data["dados"]
        return {
            "id": law["id"],
            "code": "{} {}/{}".format(
                law["siglaTipo"],
                law["numero"],
                law["ano"]),
            "description": law["ementa"],
            "created_at": datetime.strptime(
                law["dataApresentacao"],
                "%Y-%m-%dT%H:%M"),
            "status": law["statusProposicao"]["descricaoSituacao"]
        }

    def get_proposition_votes_by_id(self, proposition_id):
        response = requests.get(
            "https://www.camara.leg.br/SitCamaraWS/Proposicoes.asmx/ObterVotacaoProposicaoPorID",
            params={
                "idProposicao": proposition_id
            })
        data = xmltodict.parse(response.content.decode())
        votations = data.get("proposicao").get("Votacoes").get("Votacao")

        votes = []
        for vote in votations[0]["votos"]["Deputado"]:
            votes.append({
                "vote": True if vote["@Voto"].replace(" ", "") == "Sim" else False,
                "party": vote["@Partido"].replace(" ", ""),
                "politician": {
                    "name": vote["@Nome"],
                    "external_id": vote["@ideCadastro"]
                }
            })

        votes_by_party = {}
        votes_by_result = {"approved": 0, "rejected": 0}
        for vote in votes:
            vote_type = "rejected"
            if vote["vote"]:
                vote_type = "approved"

            if vote["party"] not in votes_by_party:
                votes_by_party[vote["party"]] = {
                    "approved": 0,
                    "rejected": 0
                }

            votes_by_result[vote_type] += 1
            votes_by_party[vote["party"]][vote_type] += 1

        return votes, votes_by_party, votes_by_result

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
