import logging.config
from optparse import OptionParser
import os
from src.config.load_config import get_config_map
import threading
import glob
import csv
import shutil
import xml.etree.ElementTree as ET


workdir = os.path.dirname(
    os.path.dirname(os.path.dirname(__file__)))  # nopep8
if "lib" == os.path.basename(workdir):
    workdir = os.path.dirname(workdir)

config_map = get_config_map()
bad_file_list = []


def _handle_cmd_line(args=None):
    parser = OptionParser()

    parser.add_option("--id", dest="id", action="store",
                      type="string", default="0",
                      help="id use guard and create log file")
    parser.add_option("--logconfig", dest="logconfig", action="store",
                      type="string",
                      default=os.path.join(
                          workdir, 'etc', 'change_xml_path.log.conf'),
                      help="log config file [%default]")
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
    if not _options.xml_path:
        logging.error(f"xml_path param is None or empty, please check it.")
        return False
    return True


def change_xml_path(xml_list, output_xml_path):
    try:
        for xml_file in xml_list:
            try:
                xml_name = os.path.basename(xml_file)
                new_xml_path = os.path.join(output_xml_path, xml_name)
                shutil.copy(xml_file, new_xml_path)
                doc = ET.parse(new_xml_path)
                root = doc.getroot()
                find_filename = root.find('filename')
                logging.info(find_filename.text)
                find_path = root.find('path')
                logging.info(find_path.text)
                new_path = os.path.join(os.path.dirname(find_path.text), find_filename.text)
                find_path.text = new_path
                doc.write(new_xml_path)
            except Exception as e:
                logging.exception(e)
                bad_file_list.append(
                    [
                        xml_file, f"path转换报错:{e}"
                    ]
                )
    except Exception as e:
        logging.exception(e)


def process(options):
    try:
        if not os.path.exists(options.output_path):
            os.mkdir(options.output_path)

        output_xml_path = os.path.join(options.output_path, "xml_labels")
        if not os.path.exists(output_xml_path):
            os.mkdir(output_xml_path)

        xml_list = glob.glob(os.path.join(options.xml_path, "*"))
        sub_xml_size = int(len(xml_list) / 8)
        all_thead_list = [
            threading.Thread(target=change_xml_path, args=[xml_list[:sub_xml_size], output_xml_path]),
            threading.Thread(target=change_xml_path, args=[xml_list[sub_xml_size:sub_xml_size * 2], output_xml_path]),
            threading.Thread(target=change_xml_path, args=[xml_list[sub_xml_size * 2:sub_xml_size * 3], output_xml_path]),
            threading.Thread(target=change_xml_path, args=[xml_list[sub_xml_size * 3:sub_xml_size * 4], output_xml_path]),
            threading.Thread(target=change_xml_path, args=[xml_list[sub_xml_size * 4:sub_xml_size * 5], output_xml_path]),
            threading.Thread(target=change_xml_path, args=[xml_list[sub_xml_size * 5:sub_xml_size * 6], output_xml_path]),
            threading.Thread(target=change_xml_path, args=[xml_list[sub_xml_size * 6:sub_xml_size * 7], output_xml_path]),
            threading.Thread(target=change_xml_path, args=[xml_list[sub_xml_size * 7:], output_xml_path]),
        ]

        for th in all_thead_list:
            th.start()

        for th in all_thead_list:
            th.join()

        bad_dir = os.path.join(options.output_path, "bad_dir")
        if not os.path.exists(bad_dir):
            os.mkdir(bad_dir)

        bad_file = open(os.path.join(bad_dir, "bad_file"), "w", newline="", encoding="utf-8")
        csv_writer = csv.writer(bad_file)
        for row in bad_file_list:
            csv_writer.writerow(row)
            bad_file.flush()
        bad_file.close()

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
    logging.info(f"开始处理 {options.xml_path} 标注文件")
    process(options)
    logging.info(f"处理结束")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"执行报错：")
        logging.exception(e)
        exit(-1)





