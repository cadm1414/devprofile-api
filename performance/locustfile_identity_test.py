from locust import HttpUser, task, between
from common.utils import get_auth_headers
from identity_tests.identity_flow import get_me, get_user_by_id

class APIUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):        
        self.client.base_url = f"{self.host}/api/v1"
        self.token = get_auth_headers(self)

    @task
    def test_profile(self):      
        
        if self.token:
            get_me(self, self.token)

    @task
    def test_get_user(self):
        if self.token:
            user_id = self.get_random_user_id()
            get_user_by_id(self, self.token, user_id=user_id)

    def get_random_user_id(self):        
        import random
        return random.randint(1, 10)
