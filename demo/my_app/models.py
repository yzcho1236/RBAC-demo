from django.db import models


# Create your models here.
class Customer(models.Model):
    id = models.AutoField('id', primary_key=True)
    nr = models.CharField('customer nr', max_length=300, db_index=True, unique=True)
    name = models.CharField('name', max_length=300, primary_key=False, db_index=True)
    area = models.CharField('area', max_length=300, db_index=True, null=True, blank=True)
    address = models.CharField('address', max_length=300, db_index=True, null=True, blank=True)

    class Meta:
        db_table = 'customer'
        permissions = (('just test','测试一下'),)


