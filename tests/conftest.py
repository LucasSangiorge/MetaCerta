import os


# Antes de importar o app: os testes nunca usam o banco do .env (Neon).
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SECRET_KEY"] = "chave-somente-para-testes-com-32-bytes-ou-mais"

from collections.abc import Callable, Generator  # noqa: E402
from datetime import date  # noqa: E402
from decimal import Decimal  # noqa: E402

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import Session, sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from app.core.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.modules.currency import service as currency_service  # noqa: E402
from app.modules.currency.schema import FrankfurterRate  # noqa: E402


engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSession = sessionmaker(bind=engine, autoflush=False)

PASSWORD = "senha-segura-123"


@pytest.fixture
def db() -> Generator[Session, None, None]:
    Base.metadata.create_all(engine)
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


@pytest.fixture
def client(db: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        try:
            yield db
        finally:
            # Igual ao get_db real (que fecha a sessão): o que não foi
            # commitado é descartado ao fim da requisição.
            db.rollback()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def exchange_api_offline(monkeypatch: pytest.MonkeyPatch) -> None:
    """Por padrão a API de câmbio está "fora": nenhum teste acessa a internet."""

    def offline(base: str, quote: str) -> FrankfurterRate:
        raise currency_service.ExchangeRateUnavailableError("API simulada fora do ar")

    monkeypatch.setattr(currency_service, "get_latest_rate", offline)


@pytest.fixture
def exchange_rate(monkeypatch: pytest.MonkeyPatch) -> Callable[[str], None]:
    """Simula a API de câmbio devolvendo a cotação informada."""

    def set_rate(rate: str, rate_date: date = date(2026, 11, 6)) -> None:
        def fake(base: str, quote: str) -> FrankfurterRate:
            return FrankfurterRate(
                date=rate_date, base=base, quote=quote, rate=Decimal(rate)
            )

        monkeypatch.setattr(currency_service, "get_latest_rate", fake)

    return set_rate


@pytest.fixture
def create_user(client: TestClient) -> Callable[[str], dict[str, str]]:
    """Cadastra um usuário, faz login e devolve o header de autenticação."""

    def _create(email: str = "ana@example.com") -> dict[str, str]:
        client.post(
            "/users", json={"name": "Ana", "email": email, "password": PASSWORD}
        )
        response = client.post(
            "/auth/login", data={"username": email, "password": PASSWORD}
        )
        return {"Authorization": f"Bearer {response.json()['access_token']}"}

    return _create


@pytest.fixture
def auth(create_user: Callable[[str], dict[str, str]]) -> dict[str, str]:
    return create_user("ana@example.com")


@pytest.fixture
def account(client: TestClient, auth: dict[str, str]) -> dict:
    response = client.post(
        "/accounts", json={"name": "Reserva", "currency": "BRL"}, headers=auth
    )
    return response.json()
