import logging
import os
from src.process.result_store import ResultStore
from src.config.load_config import get_config_map
from PIL import Image
import threading
from src.utils.get_xml import GetXML


class ImageAction(object):

    def __init__(self, sub_image_list, xml_list):
        self.image_list = sub_image_list
        self.xml_list = xml_list
        self.result_store = ResultStore()
        self.config_map = get_config_map()

    def image_check(self):
        try:
            for img in self.image_list:
                try:
                    assert self.check_image_suffix(img)
                    assert self.check_file_size(img)
                    assert self.check_image_right(img)
                    assert self.check_image_with_xml(img)
                except Exception as _e:
                    continue
        except Exception as e:
            logging.exception(e)

    def check_image_suffix(self, image_path):
        """
        检查文件后缀名
        """
        try:
            image_suffix = os.path.splitext(image_path)[1].lstrip(".")
            if image_suffix not in self.config_map["image_suffix_support_list"]:
                logging.error(f"检测到图片：{image_path}, 暂不支持图片格式为{image_suffix}")
                self.result_store.bad_image_list.append([
                    image_path, f"暂不支持图片格式为{image_suffix}"
                ])
                return False
            return True
        except Exception as e:
            logging.exception(e)

    def check_file_size(self, file_path):
        """
        检查图片文件大小
        """
        try:
            file_size = os.path.getsize(file_path)
            if not file_size:
                logging.error(f"文件{file_path}大小为：{file_size}B")
                self.result_store.bad_image_list.append([
                    file_path, f"文件大小为0B"
                ])
                return False
            return True
        except Exception as e:
            logging.exception(e)

    def check_image_right(self, image_path):
        """
        检查图片文件是否损坏
        """
        try:
            Image.open(image_path).load()
        except OSError as e:
            logging.error(f"图片{image_path}格式已损坏")
            self.result_store.bad_image_list.append([
                image_path, f"图片{image_path}格式已损坏"
            ])
            return False
        return True

    def _check_image_with_xml(self, image_path, sub_xml_list):
        tmp_xml_path_list = []  # 判断文件名前缀符合的文件名逻辑
        image_name = os.path.basename(os.path.splitext(image_path)[0])
        expect_xml_name = f"{image_name}.xml"
        for sub_xml in sub_xml_list:
            if expect_xml_name == os.path.basename(sub_xml):
                self.result_store.img_xml_map[image_path].append(sub_xml)
                return
            if os.path.basename(sub_xml).startswith(image_name):
                tmp_xml_path_list.append(sub_xml)

        # 走到这里，说明没有找到完全匹配的xml和img文件名
        if tmp_xml_path_list:
            self.result_store.img_xml_map[image_path].extend(tmp_xml_path_list)

    def check_image_with_xml(self, image_path):
        """
        检查是否有和img相符的xml
        """
        try:
            self.result_store.img_xml_map[image_path] = []
            sub_xml_size = int(len(self.xml_list) / 5)

            thread_list = [
                threading.Thread(target=self._check_image_with_xml, args=[image_path, self.xml_list[:sub_xml_size]]),  # nopep8
                threading.Thread(target=self._check_image_with_xml, args=[image_path, self.xml_list[sub_xml_size:sub_xml_size*2]]),  # nopep8
                threading.Thread(target=self._check_image_with_xml, args=[image_path, self.xml_list[sub_xml_size*2:sub_xml_size*3]]),  # nopep8
                threading.Thread(target=self._check_image_with_xml, args=[image_path, self.xml_list[sub_xml_size*3:sub_xml_size*4]]),  # nopep8
                threading.Thread(target=self._check_image_with_xml, args=[image_path, self.xml_list[sub_xml_size*4:]])  # nopep8
            ]
            for th in thread_list:
                th.start()

            for th in thread_list:
                th.join()
            if not self.result_store.img_xml_map[image_path]:
                logging.error(f"图片{image_path}没有找到对应的xml文件")
                self.result_store.bad_image_list.append([
                    image_path, f"图片{image_path}没有找到对应的xml文件"
                ])
                return False
            tmp_xml_list = self.result_store.img_xml_map[image_path]
            for sub_xml in tmp_xml_list:
                try:
                    assert self.check_xml_suffix(sub_xml)
                    assert self.check_file_size(sub_xml)
                    assert self.check_xml_right(sub_xml)
                except Exception as _e:
                    self.result_store.img_xml_map[image_path].pop(sub_xml)
                    continue
            return True
        except Exception as e:
            logging.exception(e)

    def check_xml_suffix(self, xml_path):
        """
        检测xml文件后缀名
        """
        try:
            xml_suffix = os.path.splitext(xml_path)[1].lstrip(".")
            if "xml" != xml_suffix:
                logging.error(f"文件{xml_path}不是xml文件")
                self.result_store.bad_image_list.append([
                    xml_path, f"文件{xml_path}不是xml文件"
                ])
                return False
            return True
        except Exception as e:
            logging.exception(e)

    def check_xml_right(self, xml_path):
        """
        检查xml是否损坏
        """
        try:
            xml_parser = GetXML()
            if not xml_parser.Read(xml_path):
                # 读取xml报错，即表示xml格式错误
                logging.error(f"xml文件{xml_path}格式错误")
                self.result_store.bad_image_list.append([
                    xml_path, f"xml文件{xml_path}格式错误"
                ])
                return False
            return True
        except Exception as e:
            logging.exception(e)
