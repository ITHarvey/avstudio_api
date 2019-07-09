from .scene import SceneV2


class Scenes(object):
    def __init__(self, api_access):
        self._api_access = api_access

    def add(self, scene):
        """
        covers: POST /front/api/v1t/scenes
        """
        scene_description = scene.json()
        scene_description["SceneID"] = None
        r = self._api_access.http_post_data("scenes", scene_description).json()
        return self.get(r["ID"])

    def update(self, scene):
        """
        covers: PUT /front/api/.../scenes
        """
        id = scene.id
        return self._api_access.http_put_data("scenes/%s"%id, scene.json()).json()
        
    def save(self, scene):
        """
        covers: POST /front/api/v1t/scenes
        """
        return self._api_access.http_post_data("scenes", scene.json()).json()

    def get(self, scene_id):
        """
        covers: GET /front/api/v1t/scenes/{scene}
        """
        sj = self._api_access.http_get("scenes/%s" % scene_id).json()
        scene = SceneV2()
        scene.loadJson(sj)
        return scene

    def get_all(self):
        """
        covers: GET /front/api/v1t/scenes
        """
        scenes = []
        for sd in self._api_access.http_get("scenes").json():
            scenes.append(self.get(sd["SceneID"]))

        return scenes

    def get_all_ids(self):
        """
        covers: GET /front/api/v1t/scenes
        """
        r = self._api_access.http_get("scenes")
        return [s['SceneID'] for s in r.json()]

    def delete_by_id(self, scene_id):
        """
        covers: DELETE /front/api/v1t/scenes/{scene}
        """
        return self._api_access.http_delete("scenes/" + scene_id).json()

    def delete_all(self):
        for id in self.get_all_ids():
            self.delete_by_id(id)

    def delete(self, scene):
        return self.delete_by_id(scene.id)

    def batch_set(self, scene_ids, preroll=None, postroll=None):
        """
        covers: POST /front/api/v1t/scenes/rolls
        """
        rolls = {
            "Scenes": scene_ids,
        }

        if preroll is not None:
            rolls["Preroll"] = {"ID": preroll}

        if postroll is not None:
            rolls["Postroll"] = {"ID": postroll}

        self._api_access.http_post_data("scenes/rolls", rolls)
