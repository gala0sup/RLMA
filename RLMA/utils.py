import pathlib

from plyer import storagepath

RLMAPATH = pathlib.Path(pathlib.Path(__file__).parent)

APPLICATION_DIR = storagepath.get_application_dir()

request_headers = {
    "useragent": "RLMA (https://github.com/gala0sup/RLMA) Mozilla/5.0 (Linux; Android 8.0.0; SM-G960F Build/R16NW) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.84 Mobile Safari/537.36"
}

font_path = RLMAPATH / "plugins" / "fonts"
