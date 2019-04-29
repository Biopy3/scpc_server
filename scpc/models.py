from django.db import models

# Create your models here.
class Record(models.Model):
    fastafile = models.FileField(upload_to ='scpc/recordsfile/')
    newickfile = models.FileField(upload_to ='scpc/recordsfile/')
    access_code = models.CharField(max_length=15,primary_key = True,default = '')
    resultfile = models.FileField(default='')