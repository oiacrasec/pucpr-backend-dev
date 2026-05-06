from app.core.security import PasswordHasher


def test_password_hasher_verifies_hash():
    hasher = PasswordHasher()

    hashed_password = hasher.hash("Abcdef1!")

    assert hashed_password != "Abcdef1!"
    assert hasher.verify("Abcdef1!", hashed_password) is True
    assert hasher.verify("wrong-password", hashed_password) is False
