import shutil
import threading
import logging
import csv
import os
from src.utils.get_md5 import md5_convert
import xml.etree.ElementTree as ET


workdir = os.path.dirname(
    os.path.dirname(os.path.dirname(__file__)))  # nopep8
if "lib" == os.path.basename(workdir):
    workdir = os.path.dirname(workdir)


class ResultStore(object):

    _instance_lock = threading.Lock()
    bad_image_list = []
    img_xml_map = {}

    def __new__(cls, *args, **kwargs):
        if not hasattr(ResultStore, "_instance"):
            with ResultStore._instance_lock:
                ResultStore._instance = super(ResultStore, cls).__new__(cls, *args, **kwargs)
        return ResultStore._instance

    def writer_bad_info_to_file(self):
        try:
            bad_path = os.path.join(workdir, "var", "bad")
            if not os.path.exists(bad_path):
                os.mkdir(bad_path)
            bad_file_path = os.path.join(bad_path, "bad_file")
            bad_file = open(os.path.join(bad_path, "bad_file"), "w", newline="", encoding="utf-8")
            logging.info(f"save bad info to bad file: {bad_file_path}")
            csv_writer = csv.writer(bad_file)
            for sub_info in ResultStore.bad_image_list:
                csv_writer.writerow(sub_info)
                bad_file.flush()

            bad_file.close()
            logging.info(f"save bad info to bad file: {bad_file_path} finished..........")
        except Exception as e:
            logging.exception(e)

    def convert_path(self, path):
        seps = r'\/'
        sep_other = seps.replace(os.sep, '')
        return path.replace(sep_other, os.sep) if sep_other in path else path

    def file_rename_and_move(self, output_path):
        if not os.path.exists(output_path):
            os.mkdir(output_path)
        output_image_dir = self.convert_path(os.path.join(output_path, "images"))
        output_xml_dir = self.convert_path(os.path.join(output_path, "xml_labels"))
        if not os.path.exists(output_image_dir):
            os.mkdir(output_image_dir)
        if not os.path.exists(output_xml_dir):
            os.mkdir(output_xml_dir)

        for img_file in ResultStore.img_xml_map.keys():
            try:
                if not ResultStore.img_xml_map[img_file]:
                    logging.error(f"图片{img_file}没有找到对应的图片")
                new_img_name = md5_convert(img_file)
                img_suffix = os.path.splitext(img_file)[1].lstrip(".")
                new_img_path = os.path.join(output_image_dir, f"{new_img_name}.{img_suffix}")
                shutil.copy(img_file, new_img_path)

                old_xml_path = ResultStore.img_xml_map[img_file][0]  # 不考虑匹配到多个的情况，默认取第一个
                new_xml_path = os.path.join(output_xml_dir, f"{new_img_name}.xml")
                shutil.copy(old_xml_path, new_xml_path)
                doc = ET.parse(new_xml_path)
                root = doc.getroot()
                find_filename = root.find('filename')
                find_filename.text = f"{new_img_name}.{img_suffix}"
                find_path = root.find('path')
                find_path.text = new_img_path

                doc.write(new_xml_path)
            except Exception as e:
                logging.error(f"处理图片文件: {img_file} 失败.")
                logging.exception(e)
