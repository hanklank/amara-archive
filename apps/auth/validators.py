from django.conf import settings
from django.forms import ValidationError
from django.utils.translation import ugettext_lazy as _
from zxcvbn import zxcvbn

class PasswordStrengthValidator(object):
    """Validator for ensuring strong (enough) passwords.

    Uses dropbox's zxcvbn for algorithmic validation over arbitrary character
    requirements.
    """
    def __init__(self, min_length=8):
        self.min_length = min_length

    def validate(self, password, user=None):
        # enforce minimum length
        if len(password) < self.min_length:
            raise ValidationError(
                _("Password must contain at least %(min_length)d characters."),
                code='password-too-short',
                params={'min_length': self.min_length},
            )

        results = zxcvbn(password, user_inputs=[])  # TODO: get user inputs from form
        score = results['score']
        warning = results['feedback'].get('warning', None)
        suggestions = results['feedback'].get('suggestions', None)
        # enforce password strength
        if not score > settings.MINIMUM_PASSWORD_SCORE:
            error_message = "Password not strong enough."
            if warning:
                error_message += "\n{}".format(warning)
            if suggestions:
                error_message += "\n{}".format(suggestions[0])
            raise ValidationError(_(error_message), code='weak-password')
