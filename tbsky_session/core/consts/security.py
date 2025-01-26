from enum import Enum

__all__ = ["LoginProviderEnum"]


class LoginProviderEnum(str, Enum):
    GOOGLE = "google"
    EMIAL = "none"
    FACEBOOK = "facebook"
