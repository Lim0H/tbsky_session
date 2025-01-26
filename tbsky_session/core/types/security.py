from pydantic import SecretStr

__all__ = ["PasswordStr"]


class PasswordStr(SecretStr):
    """Pydantic type for password"""

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

    def validate(self):
        v = self.get_secret_value()
        if not isinstance(v, str):
            raise TypeError("string required")

        if len(v) < self.min_length:
            raise ValueError(f"length should be at least {self.min_length}")

        if self.includes_numbers and not any(char.isdigit() for char in v):
            raise ValueError("PasswordStr should have at least one numeral")

        if self.includes_uppercase and not any(char.isupper() for char in v):
            raise ValueError("PasswordStr should have at least one uppercase letter")

        if self.includes_lowercase and not any(char.islower() for char in v):
            raise ValueError("PasswordStr should have at least one lowercase letter")

        if self.includes_special_chars and not any(
            char in self.special_chars for char in v
        ):
            raise ValueError(
                f"PasswordStr should have at least one of the symbols {self.special_chars}"
            )

        return v
