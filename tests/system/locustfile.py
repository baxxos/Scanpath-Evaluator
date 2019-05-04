from locust import HttpLocust, TaskSet, task
import json


class UserBehavior(TaskSet):
    @task(1)
    def index(self):
        self.client.get("/")

    @task(1)
    def get_dataset(self):
        self.client.get("/api/dataset?datasetId=35")

    @task(1)
    def get_task(self):
        self.client.get("/api/task?taskId=2")

    @task(1)
    def get_data_tree(self):
        self.client.get("/api/user/get_data_tree?userId=1")

    @task(1)
    def calc_common_scanpath(self):
        self.client.post(
            "/api/scanpath/sta",
            json.dumps({"excludedScanpaths": [], "taskId": 2})
        )


class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait = 2000
    max_wait = 2000
