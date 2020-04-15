from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from model_utils.models import TimeStampedModel

from .utils import get_attachment_filename
from .managers import AttachmentRelationshipManager


class Attachment(TimeStampedModel):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=255, null=True, blank=True)
    file = models.FileField(upload_to=get_attachment_filename)

    @property
    def file_type(self):
        ext = self.file.name.split('.')[-1]
        return ext

    @property
    def json(self):
        data = {
            'id': self.id,
            'name': self.name,
            'file_type': self.file_type,
            'url': self.file.url,
        }
        return data


class AttachmentRelationship(TimeStampedModel):
    # Content-object field
    content_type = models.ForeignKey(ContentType, null=True, on_delete=models.SET_NULL)
    object_id = models.IntegerField()
    content_object = GenericForeignKey(ct_field='content_type', fk_field='object_id')

    # Metadata about the attachment
    attachment = models.ForeignKey(Attachment, null=True, on_delete=models.SET_NULL)

    # Manager
    objects = AttachmentRelationshipManager()