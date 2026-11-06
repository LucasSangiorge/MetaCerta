from tests.conftest import PASSWORD


def test_cadastro_nao_devolve_a_senha(client):
    response = client.post(
        "/users",
        json={"name": "Ana", "email": "ana@example.com", "password": PASSWORD},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "ana@example.com"
    assert "password" not in body
    assert "hashed_password" not in body


def test_email_duplicado_responde_409(client):
    data = {"name": "Ana", "email": "ana@example.com", "password": PASSWORD}
    client.post("/users", json=data)

    response = client.post("/users", json=data)

    assert response.status_code == 409


def test_login_com_senha_errada_responde_401(client):
    client.post(
        "/users",
        json={"name": "Ana", "email": "ana@example.com", "password": PASSWORD},
    )

    response = client.post(
        "/auth/login", data={"username": "ana@example.com", "password": "errada123"}
    )

    assert response.status_code == 401


def test_users_me_com_token(client, auth):
    response = client.get("/users/me", headers=auth)

    assert response.status_code == 200
    assert response.json()["email"] == "ana@example.com"


def test_rota_protegida_sem_token_responde_401(client):
    assert client.get("/users/me").status_code == 401
    assert client.get("/goals").status_code == 401


def test_token_invalido_responde_401(client):
    response = client.get("/users/me", headers={"Authorization": "Bearer abc.def"})

    assert response.status_code == 401
