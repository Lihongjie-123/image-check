import logging.config
import time
from optparse import OptionParser
import os
import csv
from src.config.load_config import get_config_map
from src.process.image_action import ImageAction
import threading
import glob
from src.process.result_store import ResultStore


workdir = os.path.dirname(
    os.path.dirname(os.path.dirname(__file__)))  # nopep8
if "lib" == os.path.basename(workdir):
    workdir = os.path.dirname(workdir)

config_map = get_config_map()


def _handle_cmd_line(args=None):
    parser = OptionParser()

    parser.add_option("--id", dest="id", action="store",
                      type="string", default="0",
                      help="id use guard and create log file")
    parser.add_option("--logconfig", dest="logconfig", action="store",
                      type="string",
                      default=os.path.join(
                          workdir, 'etc', 'log.conf'),
                      help="log config file [%default]")
    parser.add_option("--image-path", dest="image_path", action="store",
                      type="string",
                      help="the path of image file")
    parser.add_option("--xml-path", dest="xml_path", action="store",
                      type="string",
                      help="the path of xml file")
    parser.add_option("--output-path", dest="output_path", action="store",
                      type="string", default=os.path.join(workdir, "var", "output"),
                      help="the path of xml file")
    (options, args) = parser.parse_args(args=args)
    return options, args


def _valid_options(_options):
    # TODO(lihongjie): 后面可能增加其他参数，用作参数检查
    if not _options.image_path:
        logging.error(f"image_path param is None or empty, please check it.")
        return False
    if not _options.xml_path:
        logging.error(f"xml_path param is None or empty, please check it.")
        return False
    return True


def deal_image_with_xml(sub_image_list, xml_list):
    image_action = ImageAction(sub_image_list, xml_list)
    image_action.image_check()


def process(options):
    try:
        image_list = glob.glob(os.path.join(options.image_path, "*"))
        xml_list = glob.glob(os.path.join(options.xml_path, "*"))
        sub_img_size = int(len(image_list) / 4)
        all_thead_list = [
            threading.Thread(target=deal_image_with_xml, args=[image_list[:sub_img_size], xml_list]),
            threading.Thread(target=deal_image_with_xml, args=[image_list[sub_img_size:sub_img_size*2], xml_list]),
            threading.Thread(target=deal_image_with_xml, args=[image_list[sub_img_size*2:sub_img_size*3], xml_list]),
            threading.Thread(target=deal_image_with_xml, args=[image_list[sub_img_size*3:], xml_list])
        ]

        for th in all_thead_list:
            th.start()

        for th in all_thead_list:
            th.join()

        result_store = ResultStore()
        result_store.writer_bad_info_to_file()
        result_store.file_rename_and_move(options.output_path)

    except Exception as e:
        logging.exception(e)


def main():
    options, _args = _handle_cmd_line()
    if options.logconfig:
        defaults = {"id": options.id}
        logging.config.fileConfig(options.logconfig, defaults)
    if not _valid_options(options):
        logging.error("options:\n" +
                      '\n'.join('%s = %s' %
                                (d, getattr(options, d))
                                for d in options.__dict__))
        return
    logging.info(f"开始处理 {options.image_path} 图片，开始处理 {options.xml_path} 标注文件")
    process(options)
    logging.info(f"处理结束")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"执行报错：")
        logging.exception(e)
        exit(-1)
