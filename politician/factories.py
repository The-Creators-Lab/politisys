from politician.models import Politician
from politician.services import CongressService, SenateService


def CongressServiceFactory(role):
    if role == Politician.DEPUTY or role == Politician.DEPUTY.lower():
        return CongressService()
    elif role == Politician.SENATOR or role == Politician.SENATOR.lower():
        return SenateService()

    return None
