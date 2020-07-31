from plyer import storagepath
import pathlib

RLMAPATH = pathlib.Path(pathlib.Path(__file__).parent)
APPLICATION_DIR = storagepath.get_application_dir()

