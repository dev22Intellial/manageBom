from django.db import models
from django.contrib.auth.models import User

class Part(models.Model):
    mpn = models.CharField(max_length=255)
    manufacturer = models.CharField(max_length=255)

    class Meta:
        unique_together = ('mpn', 'manufacturer')

    def __str__(self):
        return f"{self.manufacturer} - {self.mpn}"

class BOMFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='boms/')
    is_master = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class BOMEntry(models.Model):
    bom_file = models.ForeignKey(BOMFile, on_delete=models.CASCADE, related_name='entries')
    part = models.ForeignKey(Part, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    reference_designators = models.CharField(max_length=1000)

    def __str__(self):
        return f"{self.part} in {self.bom_file.name}"