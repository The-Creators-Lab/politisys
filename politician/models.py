from django.db import models
from party.models import Party


class Politician(models.Model):
    DEPUTY = "Role:Deputy"
    SENATOR = "Role:Senator"
    ROLES = (
        (DEPUTY, "Deputado"),
        (SENATOR, "Senador"),
    )

    picture = models.CharField(max_length=250, null=True, blank=True)
    name = models.CharField(max_length=150)
    role = models.CharField(
        max_length=50, choices=ROLES, null=True, blank=True)
    party = models.ForeignKey(
        Party, on_delete=models.CASCADE, null=True, blank=True)
    external_id = models.CharField(max_length=15, null=True, blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def get_role(self):
        return self.role if self.role else "-"

    def __str__(self):
        if self.party:
            return "{}: {}".format(self.party.initials, self.name)

        return self.name
