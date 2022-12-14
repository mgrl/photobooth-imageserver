from pydantic import BaseSettings
from typing import Any
from pathlib import Path
from datetime import datetime
from typing import Annotated
from pydantic import BaseModel, BaseSettings, Field, PrivateAttr
import os
import json
import logging
logger = logging.getLogger(__name__)

CONFIG_FILENAME = "./config/config.json"


class GroupCommon(BaseModel):
    '''Docstring for SubModelCommon'''
    CAPTURE_CAM_RESOLUTION:     tuple[int, int] = (4656, 3496)
    CAPTURE_VIDEO_RESOLUTION:   tuple[int, int] = (1280, 720)
    PREVIEW_CAM_RESOLUTION:     tuple[int, int] = (2328, 1748)
    PREVIEW_VIDEO_RESOLUTION:   tuple[int, int] = (1280, 720)
    LORES_QUALITY:              int = 80
    THUMBNAIL_QUALITY:          int = 60
    PREVIEW_QUALITY:            int = 75
    HIRES_QUALITY:              int = 90
    PREVIEW_SCALE_FACTOR:       tuple[int, int] = (1, 4)
    # possible scaling factors (TurboJPEG.scaling_factors)   (nominator, denominator)
    # limitation due to turbojpeg lib usage.
    # ({(13, 8), (7, 4), (3, 8), (1, 2), (2, 1), (15, 8), (3, 4), (5, 8), (5, 4), (1, 1),
    # (1, 8), (1, 4), (9, 8), (3, 2), (7, 8), (11, 8)})
    # example: (1,4) will result in 1/4=0.25=25% down scale in relation to the full resolution picture
    THUMBNAIL_SCALE_FACTOR:     tuple[int, int] = (1, 8)
    # possible scaling factors (TurboJPEG.scaling_factors)   (nominator, denominator)
    # limitation due to turbojpeg lib usage.
    # ({(13, 8), (7, 4), (3, 8), (1, 2), (2, 1), (15, 8), (3, 4), (5, 8), (5, 4), (1, 1),
    # (1, 8), (1, 4), (9, 8), (3, 2), (7, 8), (11, 8)})
    # example: (1,4) will result in 1/4=0.25=25% down scale in relation to the full resolution picture

    PREVIEW_PREVIEW_FRAMERATE_DIVIDER: int = 1
    EXT_DOWNLOAD_URL: str = "http://dl.qbooth.net/{filename}"

    CAPTURE_EXPOSURE_MODE: str = "short"
    # tuning file location: /usr/share/libcamera/ipa/raspberrypi
    # arducam 16mp imx519: "imx519.json"
    # arducam 64mp hawkeye: "arducam_64mp.json"
    CAMERA_TUNINGFILE: str = "imx519.json"
    # flip camera source horizontal/vertical
    CAMERA_TRANSFORM_HFLIP: bool = False
    CAMERA_TRANSFORM_VFLIP: bool = False

    # autofocus
    # 70 for imx519 (range 0...4000) and 30 for arducam64mp (range 0...1000)
    FOCUSER_ENABLED: bool = True
    FOCUSER_MIN_VALUE: int = 300
    FOCUSER_MAX_VALUE: int = 3000
    FOCUSER_DEF_VALUE: int = 800
    FOCUSER_STEP: int = 50
    # results in max. 1/0.066 fps autofocus speed rate (here about 15fps)
    FOCUSER_MOVE_TIME: float = 0.028
    FOCUSER_JPEG_QUALITY: int = 80
    FOCUSER_ROI: tuple[float, float, float, float] = (
        0.2, 0.2, 0.6, 0.6)  # x, y, width, height in %
    FOCUSER_DEVICE: str = "/dev/v4l-subdev1"
    FOCUSER_REPEAT_TRIGGER: int = 5  # every x seconds trigger autofocus

    # location service
    LOCATION_SERVICE_ENABLED: bool = False
    LOCATION_SERVICE_API_KEY: str = ""
    LOCATION_SERVICE_CONSIDER_IP: bool = True
    LOCATION_SERVICE_WIFI_INTERFACE_NO: int = 0
    LOCATION_SERVICE_FORCED_UPDATE: int = 60  # every x minutes
    # retries after program start to get more accurate data
    LOCATION_SERVICE_HIGH_FREQ_UPDATE: int = 10
    # threshold below which the data is accurate enough to not trigger high freq updates (in meter)
    LOCATION_SERVICE_THRESHOLD_ACCURATE: int = 1000

    PROCESS_COUNTDOWN_TIMER: float = 3
    PROCESS_COUNTDOWN_OFFSET: float = 0.25
    PROCESS_TAKEPIC_MSG: str = "CHEEESE!"
    PROCESS_TAKEPIC_MSG_TIMER: float = 0.5
    PROCESS_AUTOCLOSE_TIMER: int = 10
    PROCESS_ADD_EXIF_DATA: bool = True

    GALLERY_ENABLE: bool = True
    GALLERY_EMPTY_MSG: str = "So boring here...?????????????<br>Let's take some pictures ????????"

    HW_KEYCODE_TAKEPIC: str = "down"
    HW_KEYCODE_TAKEWIGGLEPIC: str = None


class GroupCamera(BaseModel):
    '''Docstring for GroupCamera'''
    settings: Annotated[str, Field(description="test123")] = 'Bar'


class GroupPersonalize(BaseModel):
    '''Docstring for Personalization'''
    UI_FRONTPAGE_TEXT: str = "Hey! Lets take some pictures! :)"


class GroupDebugging(BaseModel):
    # dont change following defaults. If necessary change via argument
    DEBUG_LEVEL: str = "DEBUG"
    DEBUG_OVERLAY: bool = False

    LOGGER_CONFIG = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s %(funcName)s() L%(lineno)-4d %(message)s'
            },
            'detailed': {
                'format': '%(asctime)s [%(levelname)s] %(name)s %(funcName)s() L%(lineno)-4d %(message)s call_trace=%(pathname)s L%(lineno)-4d'

            },
        },
        'handlers': {
            'default': {
                'level': 'DEBUG',
                'formatter': 'standard',
                'class': 'logging.StreamHandler',
                # 'stream': 'ext://sys.stdout',  # Default is stderr
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'detailed',
                'filename': './log/qbooth.log',
                'maxBytes': 1024**2,
                'backupCount': 10,
            },
            'eventstream': {
                'class': '__main__.EventstreamLogHandler',
                'formatter': 'standard',
            }
        },
        'loggers': {
            '': {  # root logger
                'handlers': ['default', 'eventstream', 'file'],
                'level': 'DEBUG',
                'propagate': False
            },
            '__main__': {  # if __name__ == '__main__'
                'handlers': ['default', 'eventstream', 'file'],
                'level': 'DEBUG',
                'propagate': False
            },
            'picamera2': {
                'handlers': ['default'],
                'level': 'INFO',
                'propagate': False
            },
            'pywifi': {
                'handlers': ['default'],
                'level': 'WARNING',
                'propagate': False
            },
            'sse_starlette.sse': {
                'handlers': ['default'],
                'level': 'INFO',
                'propagate': False
            },
            'lib.Autofocus': {
                'handlers': ['default'],
                'level': 'INFO',
                'propagate': False
            },
            'transitions.core': {
                'handlers': ['default'],
                'level': 'INFO',
                'propagate': False
            },
        }
    }


class GroupColorled(BaseModel):
    '''Colorled settings for neopixel and these elements'''
    # infoled / ws2812b ring settings
    NUMBER_LEDS: int = 12
    GPIO_PIN: int = 18
    COLOR: tuple[int, int, int, int] = (255, 255, 255, 255)    # RGBW
    CAPTURE_COLOR: tuple[int, int, int, int] = (0, 125, 125, 0)  # RGBW
    MAX_BRIGHTNESS: int = 50
    ANIMATION_UPDATE: int = 70    # update circle animation every XX ms


class ConfigSettings(BaseModel):
    '''Settings class glueing all together'''

    _processed_at: datetime = PrivateAttr(
        default_factory=datetime.now)  # private attributes

    # groups -> setting items
    common: GroupCommon = GroupCommon()
    camera: GroupCamera = GroupCamera()
    colorled: GroupColorled = GroupColorled()
    debugging: GroupDebugging = GroupDebugging()

    def load(self):
        return
        # this is not working properly yet. instead only on instanciation import json like ConfigSettings(**dict)

        with open(CONFIG_FILENAME, "r") as read_file:
            loadedConfig = json.load(read_file)
            print(loadedConfig)
            # self = self.parse_obj(loadedConfig)
            # self.__dict__.update(loadedConfig)
            # self = self.copy(update=loadedConfig)
            self = ConfigSettings(**loadedConfig)

    def persist(self):
        '''Persist settings to file'''
        logger.debug(f"persist settings to json file")

        with open(CONFIG_FILENAME, "w") as write_file:
            write_file.write(self.json(indent=2))

    def deleteconfig(self):
        '''Reset to defaults'''
        logger.debug(f"settings reset to default")

        try:
            os.remove(CONFIG_FILENAME)
            logger.debug(f"deleted {CONFIG_FILENAME} file.")
        except:
            logger.info(f"delete {CONFIG_FILENAME} file failed.")


# our settings that can be imported throughout the app like # from lib.ConfigService import settings
# TODO: might wanna use LROcache functools.
settings = ConfigSettings()
try:
    with open(CONFIG_FILENAME, "r") as read_file:
        loadedConfig = json.load(read_file)
    settings = ConfigSettings(**loadedConfig)
except:
    logger.error(
        f"config file {CONFIG_FILENAME} could not be read, using defaults")

    # load defaults and persist if no file found
    settings.persist()


if __name__ == '__main__':

    settings.debugging.DEBUG_OVERLAY = True
    assert settings.debugging.DEBUG_OVERLAY is True
    settings.persist()
    with open(CONFIG_FILENAME, "r") as read_file:
        loadedConfig = json.load(read_file)
    settings = ConfigSettings(**loadedConfig)  # reread config
    assert settings.debugging.DEBUG_OVERLAY is True

    settings.debugging.DEBUG_OVERLAY = False
    settings.persist()
    with open(CONFIG_FILENAME, "r") as read_file:
        loadedConfig = json.load(read_file)
    settings = ConfigSettings(**loadedConfig)  # reread config
    assert settings.debugging.DEBUG_OVERLAY is False

    settings.debugging.DEBUG_OVERLAY = True
    settings.persist()
    with open(CONFIG_FILENAME, "r") as read_file:
        loadedConfig = json.load(read_file)
    settings = ConfigSettings(**loadedConfig)  # reread config
    assert settings.debugging.DEBUG_OVERLAY is True

    settings.deleteconfig()
    # reread config, this one is default now
    settings = ConfigSettings()
    settings.persist()
    assert settings == ConfigSettings()  # is all default?

    # print(settings)
