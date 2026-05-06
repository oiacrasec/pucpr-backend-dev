import logging

from app.core.config import Settings


def configure_logging(settings: Settings) -> None:
    """Configura o formato e o nivel de log de todo o processo."""
    log_level = logging.DEBUG if settings.environment != "production" else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
