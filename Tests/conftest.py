import pytest

from app import create_app, database


@pytest.fixture
def app(tmp_path, monkeypatch):
    """Cria o app com um banco de dados temporário (não mexe no bonsai.db)."""
    monkeypatch.setattr(database, "DB_NAME", str(tmp_path / "teste.db"))
    return create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "teste",
            "UPLOAD_FOLDER": str(tmp_path / "uploads"),
        }
    )


@pytest.fixture
def client(app):
    return app.test_client()
