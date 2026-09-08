from locust import HttpUser, between, task


class DemoUser(HttpUser):
    wait_time = between(0.1, 0.4)

    @task(4)
    def cpu_work(self):
        with self.client.get("/work", name="/work", catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"unexpected status {response.status_code}")

    @task(1)
    def health(self):
        self.client.get("/health", name="/health")
