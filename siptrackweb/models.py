from django.db import models

from storage import GridFSStorage

class AttributeFile(models.Model):
    created_on = models.DateTimeField(
        auto_now_add=True
    )
    filename = models.TextField(
        max_length=50
    )
    oid = models.TextField(
        max_length=64
    )
    file = models.FileField(
        storage=GridFSStorage(),
        upload_to='./media/'
    )