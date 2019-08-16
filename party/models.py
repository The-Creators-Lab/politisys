from django.db import models


class Party(models.Model):
    name = models.CharField(max_length=200)
    initials = models.CharField(max_length=20)
    external_id = models.CharField(max_length=15, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return "{}: {}".format(
            self.initials,
            self.name)
