from random import shuffle, randint

from locust import HttpLocust, TaskSet, task
import uuid

from locust.exception import StopLocust


class WebsiteTasks(TaskSet):
    def __init__(self, parent):
        super().__init__(parent)
        self.current_visible = []
        self.headers = {'Authorization': f'{uuid.uuid1()}+{uuid.uuid1()}'}

    def _set_current_visible(self, json_response):
        self.current_visible = [item['uri'] for item in json_response]
        print(self.current_visible)

    def on_start(self):
        self._set_current_visible(self.client.get("/movies", headers=self.headers).json())

    @task
    def feedback(self):
        shuffle(self.current_visible)

        n_liked = randint(0, len(self.current_visible))
        n_disliked = randint(0, len(self.current_visible) - n_liked)

        liked = self.current_visible[:n_liked]
        disliked = self.current_visible[n_liked:n_liked + n_disliked]
        unknown = self.current_visible[n_liked + n_disliked:len(self.current_visible)]

        result = self.client.post("/feedback", json={'liked': liked,
                                                     'disliked': disliked,
                                                     'unknown': unknown}, headers=self.headers).json()

        if 'prediction' not in result or not result['prediction']:
            self._set_current_visible(result)
        else:
            raise StopLocust()


class WebsiteUser(HttpLocust):
    task_set = WebsiteTasks
    min_wait = 10000
    max_wait = 30000
