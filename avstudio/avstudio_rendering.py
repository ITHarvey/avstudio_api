import requests


class Rendering(object):
    def __init__(self, api_access):
        self._api_access = api_access

    def get_all(self):
        """
        covers: GET /front/api/v1t/media/renders
        """
        return self._api_access.http_get("media/renders").json()

    def get_render_profiles(self):
        """
        covers: GET /front/api/v1t/media/profiles
        """

        return self._api_access.http_get("media/profiles").json()

    def start_rendering(self, scene, **kwargs):
        """
        covers: POST /front/api/v1t/media/scenes/{scene}/render
        """
        url = "media/scenes/%s/render" % scene.id
        params = {
            "locations": [],
            "bitrate": kwargs.get("bitrate", 800000),
            "frame_size": {
                "width": 640,
                "height": 360
            }
        }

        if "frame_size" in kwargs:
            params["frame_size"] = {
                "width": kwargs["frame_size"][0],
                "height": kwargs["frame_size"][1]
            }

        return self._api_access.http_post_data(url, params).json()

    def stop_rendering(self, scene, task_id):
        """
        covers: POST /front/api/v1t/media/scenes/{scene}/tasks/{task}/stop
        """
        url = "media/scenes/%s/tasks/%s/stop" % (scene.id, task_id)
        return self._api_access.http_post(url)

    def get_tasks_for_scene(self, scene):
        """
        covers: GET /front/api/v1t/media/scenes/{scene}/tasks
        """
        url = "media/scenes/%s/tasks" % scene.id
        return self._api_access.http_get(url).json()

    def get_task_for_scene_by_id(self, scene, task_id):
        """
        covers: GET /front/api/v1t/media/scenes/{scene}/tasks/{task}
        """

        url = "media/scenes/%s/tasks/%s" % (scene.id, task_id)
        return self._api_access.http_get(url).json()

    def get_tasks(self):
        """
        covers: GET /front/api/v1t/media/renders
        """
        return self._api_access.http_get("media/renders").json()

    def get_task_by_id(self, task_id):
        for f in self.get_tasks():
            if f["ID"] == task_id:
                return f

        return None

    def get_scene_thumbnail(self, scene, timestamp, filename, relative=False, out_of_scene=False, size=None):
        """
        covers: GET /front/api/v1t/media/scenes/{scene}/snapshot
        """
        if relative:
            scene_begin = float(scene.sceneRange[0])
            timestamp = scene_begin + timestamp

        oos = "yes" if out_of_scene else ""
        snapshot_url = "media/scenes/%s/snapshot?from=%f&out-of-scene=%s" % (scene.id, timestamp, oos)

        if size is not None:
            snapshot_url += "&size=%s" % size

        self._api_access.http_download_file(snapshot_url, filename)

    # API for rendered files duplicates render task API to some extent

    def get_rendered_files(self):
        """
        covers: GET /front/api/v1t/media/results
        """
        return self._api_access.http_get("media/results").json()

    def get_rendered_file_by_id(self, render_id):
        for f in self.get_rendered_files():
            if f["ID"] == render_id:
                return f

        return None

    def download_rendered_file_for_task_id(self, render_id, local_file):
        """
        covers: GET /api/v1t/media/scenes/{scene}/results/{task}
        """
        f = self.get_rendered_file_by_id(render_id)
        download_url = "media/%s" % f["Url"]
        return None if f is None else self._api_access.http_download_file(download_url, local_file)

    def download_rendered_file_for_task(self, task_desc, local_file):
        download_url = "media/%s" % task_desc["Url"]
        return self._api_access.http_download_file(download_url, local_file)

    def delete_rendered_file(self, render_id):
        """
        covers: POST /front/api/v1t/media/scenes/{scene}/tasks/{task}/remove
        """
        f = self.get_rendered_file_by_id(render_id)
        remove_url = "media/scenes/%s/tasks/%s/remove" % (f["Scene"], render_id)
        return None if f is None else self._api_access.http_post(remove_url)

    def delete_rendered_file_for_scene(self, scene, render_id):
        """
        covers: POST /front/api/v1t/media/scenes/{scene}/tasks/{task}/remove
        """
        params = {
            "s": scene.id,
            "t": render_id
        }
        post_url = "media/scenes/%(s)s/tasks/%(t)s/remove" % params
        return self._api_access.http_post(post_url)

    def share_rendered_file(self, sc, render_id):
        """
        covers: GET /front/api/v1t/media/scenes/{scene}/results/{task}/share
        """
        params = {
            "s": sc.id,
            "t": render_id
        }
        return self._api_access.http_get("media/scenes/%(s)s/results/%(t)s/share" % params).json()

    def unshare_rendered_file(self, sc, render_id):
        """
        covers: GET /front/api/v1t/media/scenes/{scene}/results/{task}/unshare
        """
        params = {
            "s": sc.id,
            "t": render_id
        }
        return self._api_access.http_get("media/scenes/%(s)s/results/%(t)s/unshare" % params).json()

    def delete_share_by_link(self, link):
        """
        covers: DELETE /front/api/v1t/shares/renders/{link}
        """
        return self._api_access.http_delete("shares%s" % link)

    def check_public_share(self, link):
        """
        covers: GET /front/api/v1t/public/shares/renders/{link}
        """
        path = self._api_access.get_full_url("public/shares%s" % link, noteam=True)
        header = {"Range": "bytes=0-100"}
        r = requests.get(path, headers=header)
        r.raise_for_status()
        return r

    def check_public_share_details(self, link):
        """
        covers: GET /front/api/v1t/public/shares/renders/{link}/details
        """
        path = self._api_access.get_full_url("public/shares%s/details" % link, noteam=True)
        r = requests.get(path)
        r.raise_for_status()
        return r
