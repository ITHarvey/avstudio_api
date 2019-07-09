import datetime

class Shot(object):
    def __init__(self, timestamp=None, layout="single", videoSources=[], audioSources=[]):
        self._videoSources = videoSources
        self._audioSources = audioSources
        self._background = None
        self._layout = layout
        self._skipped = False
        self._timestamp = timestamp
        self._videoEffects = {}

    @property
    def videoSources(self):
        return self._videoSources

    @videoSources.setter
    def videoSources(self, ids):
        self._videoSources = ids

    @property
    def audioSources(self):
        return self._audioSources

    @audioSources.setter
    def audioSources(self, ids):
        self._audioSources = ids

    @property
    def timestamp(self):
        return self._timestamp

    @timestamp.setter
    def timestamp(self, value):
        self._timestamp = value

    @property
    def skipped(self):
        return self._skipped

    @skipped.setter
    def skipped(self, value):
        self._skipped = value

    @property
    def layout(self):
        return self._layout

    @layout.setter
    def layout(self, value):
        self._layout = value

    def setVideoEffects(self, nsrc, brightness, contrast):
        if brightness == 0 and contrast == 0 and nsrc in self._videoEffects:
            del self._videoEffects[nsrc]
        else:
            self._videoEffects[nsrc] = {
                "Brightness": brightness,
                "Contrast": contrast
            }

    def setBackgroundImage(self, asset_id, asset_name):
        self.setBackground({
            "Type": "Image",
            "Image": {
                "ID": asset_id,
                "Name": asset_name
            }
        })

    def setBackgroundColor(self, color):
        self.setBackground({
            "Type": "Color",
            "Color": color
        })

    def setBackground(self, background):
        self._background = background

    def json(self):

        vsrc = [{"ID": id} for id in self._videoSources]
        vsrc = []
        for i in range(len(self._videoSources)):
            src = {"ID": self._videoSources[i]}

            if i in self._videoEffects:
                src["Effects"] = self._videoEffects[i]

            vsrc.append(src)

        res = {
            "Sources": {
                "Audio": [{"ID": id} for id in self._audioSources],
                "Video": vsrc
            },
            "Layout": self._layout,
            "Skip": self._skipped,
            "Time": self._timestamp
        }

        if self._background is not None:
            res["Sources"]["Background"] = self._background

        return res

    def loadJson(self, json_dict):
        if not isinstance(json_dict, dict):
            raise Exception("json must be a dictionary")

        self._timestamp = json_dict["Time"]
        self._skipped = json_dict["Skip"]
        self._layout = json_dict["Layout"]

        if "Audio" in json_dict["Sources"]:
            self._audioSources = [src["ID"] for src in json_dict["Sources"]["Audio"]]

        if "Video" in json_dict["Sources"]:
            self._videoSources = [src["ID"] for src in json_dict["Sources"]["Video"]]

        self._background = json_dict.get("Background", None)


class SceneV2(object):
    def __init__(self):
        self._id = None
        self._name = str(datetime.datetime.now().strftime("AUTO %H_%M_%S"))
        self._preroll = None
        self._postroll = None
        self._viewRange = (1486571400, 1486571410)
        self._sceneRange = (1486571400, 1486571410)
        self._shots = []
        self._ar = (16, 9)

    def _getAllSources(self):
        videoIds = []
        audioIds = []
        for shot in self._shots:
            videoIds += shot.videoSources
            audioIds += shot.audioSources

        videoIds = [(id, "video") for id in list(set(videoIds))]
        audioIds = [(id, "audio") for id in list(set(audioIds))]

        return [
            {
                "SourceID": src[0],
                "TimeOffset": 0,
                "SourceType": src[1],
                "Position": ""
            }
            for src in (videoIds + audioIds)
        ]

    def json(self):
        return {
            "SceneApiVersion": "2t",
            "SceneID": self._id,
            "Name": self._name,
            "Preroll": {"ID": "" or self._preroll},
            "Postroll": {"ID": "" or self._postroll},
            "Sources": self._getAllSources(),
            "ViewRange": {
                "Begin": self._viewRange[0],
                "End": self._viewRange[1]
            },
            "SceneRange": {
                "Begin": self._sceneRange[0],
                "End": self._sceneRange[1]
            },
            "Shots": [shot.json() for shot in self._shots],
            "AspectRatio": {
                "w": self._ar[0],
                "h": self._ar[1]
            }
        }

    def loadJson(self, json_dict):
        if not isinstance(json_dict, dict):
            raise Exception("json must be a dictionary")

        if json_dict["SceneApiVersion"] != "2t":
            raise Exception("Only version 2t is supported")

        self._id = json_dict["SceneID"]
        self._name = json_dict["Name"]

        if "Preroll" in json_dict:
            self.preroll = json_dict["Preroll"]["ID"]

        if "Postroll" in json_dict:
            self.postroll = json_dict["Postroll"]["ID"]

        if "AspectRatio" in json_dict:
            self.ar = json_dict["AspectRatio"]["w"], json_dict["AspectRatio"]["h"]

        self.sceneRange = json_dict["SceneRange"]["Begin"], json_dict["SceneRange"]["End"]
        self.viewRange = json_dict["ViewRange"]["Begin"], json_dict["ViewRange"]["End"]

        self._shots = []
        for shot_json in json_dict.get("Shots", []):
            shot = Shot()
            shot.loadJson(shot_json)
            self._shots.append(shot)

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def viewRange(self):
        return self._viewRange

    @viewRange.setter
    def viewRange(self, value):
        self._viewRange = (value[0], value[1])

    @property
    def sceneRange(self):
        return self._sceneRange

    @sceneRange.setter
    def sceneRange(self, value):
        self._sceneRange = (value[0], value[1])
        self._viewRange = (value[0] - 10, value[1] + 10)

    @property
    def preroll(self):
        return self._preroll

    @preroll.setter
    def preroll(self, value):
        self._preroll = value

    @property
    def postroll(self):
        return self._postroll

    @postroll.setter
    def postroll(self, value):
        self._postroll = value

    @property
    def ar(self):
        return self._ar

    @ar.setter
    def ar(self, value):
        self._ar = int(value[0]), int(value[1])  # Primitive type checking

    def addShot(self, timestamp, videoSources, audioSources):
        if timestamp is None:
            timestamp = self._sceneRange[0]

        shot = Shot(timestamp)
        shot.videoSources = videoSources
        shot.audioSources = audioSources

        self._shots.append(shot)

        self._shots = sorted(self._shots, key=lambda sh: sh.timestamp)

        return shot

    def getShotByIndex(self, idx):
        return self._shots[idx]
