from django.db import models
from django.contrib.contenttypes.models import ContentType


class AttachmentRelationshipManager(models.Manager):
    def get_or_create_attachment(self, attachment, content_object):
        content_type = ContentType.objects.get_for_model(content_object)
        return self.get_or_create(content_type=content_type, object_id=content_object.id, attachment=attachment)

    def filter_attachment(self, content_object, **kwargs):
        result = []
        content_type = ContentType.objects.get_for_model(content_object)
        ar_list = self.filter(content_type=content_type, object_id=content_object.id, **kwargs)
        for ar in ar_list:
            result.append(ar.attachment)
        return result