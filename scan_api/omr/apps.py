from django.apps import AppConfig


class OmrConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "omr"

    def ready(self):
        # Registra o suporte a HEIC/HEIF uma única vez na inicialização do processo.
        # Sem isso, imagens de iPhone (.heic) falhariam na validação do ImageField.
        from omr.services.image_io import register_heif_opener

        register_heif_opener()
