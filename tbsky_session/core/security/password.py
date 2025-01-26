from functools import cache

from passlib.context import CryptContext

__all__ = ["PasswordTools"]


@cache
def get_pwd_context():
    return CryptContext(schemes=["bcrypt"], deprecated="auto")


class PasswordTools:
    pwd_context = get_pwd_context()

    special_chars = {
        "$",
        "@",
        "#",
        "%",
        "!",
        "^",
        "&",
        "*",
        "(",
        ")",
        "-",
        "_",
        "+",
        "=",
        "{",
        "}",
        "[",
        "]",
    }

    min_length = 10
    includes_special_chars = True
    includes_numbers = True
    includes_lowercase = True
    includes_uppercase = True

    @classmethod
    def validate_password(cls, v: str):
        """
        Validate a password.

        Args:
            password: The password to validate.

        Returns:
            True if the password is valid, False otherwise.
        """
        if not isinstance(v, str):
            raise TypeError("string required")

        if len(v) < cls.min_length:
            raise ValueError(f"length should be at least {cls.min_length}")

        if cls.includes_numbers and not any(char.isdigit() for char in v):
            raise ValueError("PasswordStr should have at least one numeral")

        if cls.includes_uppercase and not any(char.isupper() for char in v):
            raise ValueError("PasswordStr should have at least one uppercase letter")

        if cls.includes_lowercase and not any(char.islower() for char in v):
            raise ValueError("PasswordStr should have at least one lowercase letter")

        if cls.includes_special_chars and not any(
            char in cls.special_chars for char in v
        ):
            raise ValueError(
                f"PasswordStr should have at least one of the symbols {cls.special_chars}"
            )
        return v

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str):
        """
        Verify a password against a hashed password.

        Args:
            plain_password: The password in plain text.
            hashed_password: The hashed password.

        Returns:
            True if the password matches, False otherwise.
        """
        return cls.pwd_context.verify(plain_password, hashed_password)

    @classmethod
    def get_password_hash(cls, password: str):
        """
        Hash a password for storing.

        Args:
            password: The password that needs a hash.

        Returns:
            A hashed version of the password.
        """
        return cls.pwd_context.hash(password)
