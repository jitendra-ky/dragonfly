from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    id: int
    email: str
    contact: str

    @property
    def first_name(self) -> str:
        """Expose contact through the built-in User field name."""
        return self.contact
