def get_me(user, token):
    response = user.client.get(
        "/identity/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    if response.status_code != 200:
        print(f"Error en /identity/me: {response.status_code} - {response.text}")

def get_user_by_id(user, token, user_id=1):
    response = user.client.get(
        f"/identity/users/{user_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    if response.status_code == 200:
        data = response.json()
        print(f"Usuario {user_id}: {data['full_name']}")
        return data
    else:
        print(f"Error en /identity/users/{user_id}: {response.status_code} - {response.text}")
        return None