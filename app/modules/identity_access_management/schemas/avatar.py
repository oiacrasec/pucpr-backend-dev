from pydantic import BaseModel


class AvatarResponse(BaseModel):
    """Payload de resposta para leitura ou upload de avatar."""

    user_id: int
    content_type: str
    size_bytes: int
    url: str
