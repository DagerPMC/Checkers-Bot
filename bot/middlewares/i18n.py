from typing import Any, Dict

from aiogram.types import TelegramObject, User
from aiogram.utils.i18n import I18n, I18nMiddleware
from aiogram.utils.i18n import gettext as _gettext


class TelegramI18nMiddleware(I18nMiddleware):
    async def get_locale(
        self, event: TelegramObject, data: Dict[str, Any]
    ) -> str:
        user: User | None = data.get("event_from_user")
        if user and user.language_code:
            lang = user.language_code.lower().split("-")[0]
            if lang in ["uk"]:
                return "uk"
            return "en"
        return self.i18n.default_locale


def gettext(singular: str, **kwargs: Any) -> str:
    text = _gettext(singular)
    if kwargs:
        return text.format(**kwargs)
    return text


def gettext_with_locale(singular: str, locale: str, **kwargs: Any) -> str:
    import gettext as py_gettext
    translations = py_gettext.translation(
        domain='messages',
        localedir='locales',
        languages=[locale],
        fallback=True
    )
    text = translations.gettext(singular)
    if kwargs:
        return text.format(**kwargs)
    return text


def setup_i18n() -> tuple[I18n, TelegramI18nMiddleware]:
    i18n = I18n(
        path="locales",
        default_locale="en",
        domain="messages",
    )

    middleware = TelegramI18nMiddleware(i18n=i18n)

    return i18n, middleware
