from locust import HttpUser, task, between
from login_tests.login_stress_flow import stress_login

class LoginStressUser(HttpUser):
    wait_time = between(0.5, 1.5)

    def on_start(self):     
        self.client.base_url = f"{self.host}/api/v1"   
        stress_login(self)

    @task
    def test_login(self):        
        stress_login(self)