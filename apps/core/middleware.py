from django.conf import settings
from django.utils.translation import activate


class LanguageMiddleware(object):
    def process_view(self, request, view, args, kwargs):
        user = request.user
        is_auth = user.is_authenticated()
        user_lang = is_auth and user.language or settings.LANGUAGE_CODE
        lang = kwargs.get('lang', request.session.get('language', user_lang))

        request.LANGUAGE_CODE = lang
        activate(lang)
