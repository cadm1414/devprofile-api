from common.utils import login_and_get_token

def stress_login(user):
    
    token = login_and_get_token(user)

    if token:        
        user.client.headers.update({"Authorization": f"Bearer {token}"})
    else:
        
        print("No se pudo obtener token en stress_login")