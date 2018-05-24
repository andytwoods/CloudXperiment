from django.contrib.auth.decorators import login_required

from .models import Attachment, AttachmentRelationship


@login_required
def attachment_upload(request, content_object=None):
    if request.method == 'POST':
        u_file = request.FILES['file']
        attachment_name = request.GET.get('attachment_name', u_file.name)
        attachment = Attachment(
            user=request.user,
            name=attachment_name,
            file=u_file
        )
        attachment.save()
        request.user.profile.avatar = attachment.file.url
        request.user.profile.save()
        if content_object:
            AttachmentRelationship.objects.get_or_create_attachment(attachment, content_object)
        return attachment.json
    return None