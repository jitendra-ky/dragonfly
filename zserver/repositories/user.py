from zserver.domain.entities import User
from zserver.models.user_profile import User as UserModel


class UserRepository:
    async def get_active_user(self, user_id: int) -> UserModel | None:
        """Return an active ORM user for websocket authentication."""
        try:
            return await UserModel.objects.aget(id=user_id, is_active=True)
        except UserModel.DoesNotExist:
            return None

    def get_by_email(self, email: str) -> UserModel:
        """Return the ORM user required by authentication workflows."""
        return UserModel.objects.get(email=email)

    def email_exists(self, email: str) -> bool:
        """Return whether a registered user has the given email."""
        return UserModel.objects.filter(email=email).exists()

    def get_or_create_google_user(self, *, email: str, contact: str) -> tuple[UserModel, bool]:
        """Get or create an active user for Google authentication."""
        user, created = UserModel.objects.get_or_create(
            email=email,
            defaults={"contact": contact, "is_active": True, "email_verified": True},
        )
        if created:
            user.set_unusable_password()
            user.save()
        return user, created

    def get_many(self, user_ids: list[int] | None = None) -> list[User]:
        """Return users as domain entities, optionally filtered by ID."""
        users = UserModel.objects.all()
        if user_ids is not None:
            users = users.filter(id__in=user_ids)
        return [self._to_entity(user) for user in users]

    def update(
        self,
        user: UserModel,
        *,
        contact: str,
        email: str,
        password: str | None,
    ) -> UserModel:
        """Update a user model and return it for response serialization."""
        user.contact = contact
        user.email = email
        if password is not None:
            user.set_password(password)
        user.save()
        return user

    @staticmethod
    def _to_entity(user: UserModel) -> User:
        return User(id=user.id, email=user.email, contact=user.contact)
