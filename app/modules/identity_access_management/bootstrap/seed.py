import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.core.security import PasswordHasher
from app.modules.identity_access_management.models.role import Role
from app.modules.identity_access_management.models.user import User
from app.modules.identity_access_management.repositories.role_repository import (
    RoleRepository,
)
from app.modules.identity_access_management.repositories.user_repository import (
    UserRepository,
)


logger = logging.getLogger(__name__)


def seed_identity_access_data(
    session: Session,
    settings: Settings,
    password_hasher: PasswordHasher,
) -> None:
    """Garante a existencia das roles padrao e do admin bootstrap."""
    role_repository = RoleRepository(session)
    user_repository = UserRepository(session)

    admin_role = role_repository.find_by_name("ADMIN")
    if admin_role is None:
        admin_role = role_repository.add(
            Role(name="ADMIN", description="System Administrator")
        )

    if role_repository.find_by_name("PREMIUM") is None:
        role_repository.add(Role(name="PREMIUM", description="Premium user"))

    if user_repository.find_by_role("ADMIN"):
        session.commit()
        return

    admin = User(
        email=settings.bootstrap_admin_email,
        password=password_hasher.hash(settings.bootstrap_admin_password),
        name=settings.bootstrap_admin_name,
    )
    admin.roles.add(admin_role)
    user_repository.add(admin)

    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        logger.warning("Bootstrap admin could not be created because the email already exists.")
