import re

import dns.resolver
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_email_domain_exists(email):
    """
    Valida se o domínio do email existe e se possui registro MX.

    Observação:
    Isso não confirma se a caixa de email existe,
    apenas se o domínio está apto a receber emails.
    """

    if not email or "@" not in email:
        raise ValidationError(_("Informe um email válido."))

    domain = email.split("@")[-1].lower().strip()

    if not domain:
        raise ValidationError(_("Informe um domínio de email válido."))

    try:
        answers = dns.resolver.resolve(domain, "MX")

        if not answers:
            raise ValidationError(_("O domínio do email não possui servidor de email válido."))

    except dns.resolver.NXDOMAIN:
        raise ValidationError(_("O domínio do email não existe."))
    except dns.resolver.NoAnswer:
        raise ValidationError(_("O domínio do email não possui registro MX."))
    except dns.resolver.NoNameservers:
        raise ValidationError(_("Não foi possível validar o domínio do email."))
    except dns.exception.Timeout:
        raise ValidationError(_("Tempo esgotado ao validar o domínio do email."))


class StrongPasswordValidator:
    """
    Validador de senha forte.

    Exige:
    - mínimo 8 caracteres;
    - pelo menos uma letra maiúscula;
    - pelo menos uma letra minúscula;
    - pelo menos um número;
    - pelo menos um caractere especial.
    """

    def validate(self, password, user=None):
        if len(password) < 8:
            raise ValidationError(
                _("A senha deve ter pelo menos 8 caracteres."),
                code="password_too_short",
            )

        if not re.search(r"[A-Z]", password):
            raise ValidationError(
                _("A senha deve conter pelo menos uma letra maiúscula."),
                code="password_no_upper",
            )

        if not re.search(r"[a-z]", password):
            raise ValidationError(
                _("A senha deve conter pelo menos uma letra minúscula."),
                code="password_no_lower",
            )

        if not re.search(r"\d", password):
            raise ValidationError(
                _("A senha deve conter pelo menos um número."),
                code="password_no_number",
            )

        if not re.search(r"[^\w\s]", password):
            raise ValidationError(
                _("A senha deve conter pelo menos um caractere especial."),
                code="password_no_special",
            )

    def get_help_text(self):
        return _(
            "A senha deve ter pelo menos 8 caracteres, incluindo uma letra maiúscula, "
            "uma letra minúscula, um número e um caractere especial."
        )