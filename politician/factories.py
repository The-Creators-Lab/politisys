from politician.models import Politician
from politician.services import CongressService, SenateService


def CongressServiceFactory(role):
    if role == Politician.DEPUTY:
        return CongressService()
    elif role == Politician.SENATOR:
        return SenateService()

    return None
