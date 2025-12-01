from django.db import models

class BOMItem(models.Model):
    reference_designators = models.CharField(max_length=255)
    quantity = models.IntegerField()
    identified_mpn = models.CharField(max_length=255, blank=True, null=True)
    identified_manufacturer = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.reference_designators} - {self.identified_mpn}"
