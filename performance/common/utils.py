def login_and_get_token(user):
    response = user.client.post(
        "/auth/access",
        json={"email": "test@gmail.com", "password": "123qweasd"}
    )
    if response.status_code == 200:
        data = response.json()
        return data.get("access_token")
    else:
        print(f"Login fallido: {response.status_code} - {response.text}")
        return None

def get_auth_headers(client, token=None):    
    if not token:
        token = login_and_get_token(client)
    if not token:        
        return {}

    return token