import os

from django.conf import settings
from django.http import FileResponse, Http404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def serve_protected_media(request, path: str):
    """
    Serve arquivos de mídia (scan_results/, exam_templates/) somente para
    usuários autenticados. Impede acesso direto a /media/ sem token JWT.

    Proteção contra path traversal: rejeita qualquer path que escape do
    MEDIA_ROOT após resolução absoluta.
    """
    media_root = os.path.abspath(settings.MEDIA_ROOT)
    requested = os.path.abspath(os.path.join(media_root, path))

    if not requested.startswith(media_root + os.sep):
        raise Http404

    if not os.path.isfile(requested):
        raise Http404

    return FileResponse(open(requested, "rb"))
