from configparser import ConfigParser
import os


workdir = os.path.dirname(
    os.path.dirname(os.path.dirname(__file__)))  # nopep8
if "lib" == os.path.basename(workdir):
    workdir = os.path.dirname(workdir)


def get_config_map():
    config_map = {}
    config = ConfigParser()
    config.read(os.path.join(workdir, "etc", "config.conf"), encoding='UTF-8')
    config_map["version"] = \
        config.get("setting", "version")
    config_map["image_suffix_support_list"] = \
        config.get("setting", "image_suffix_support_list").split(",")
    return config_map
