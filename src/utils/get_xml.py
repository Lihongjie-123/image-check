import xml.etree.ElementTree as ET
import logging


class GetXML:
    def __init__(self):
        self.root = None

    def Read(self, xml_file_name):
        try:
            tree = ET.ElementTree(file=xml_file_name)
            self.root = tree.getroot()
            return self.root
        except Exception as e:
            logging.exception(e)

    def Iter(self):
        return self.root.iter()

    def FindAll(self, tag):
        return self.root.findall(tag)

    def Find(self, tag):
        return self.root.find(tag)
