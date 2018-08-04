import configparser
import os


class PropertyManager:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read("../properties/scrapper.properties")

    def getProperty(self, propertyName):
        return self.config.get("default", propertyName)

    def getPropertyAsInteger(self, propertyName):
        return int(self.config.get("default", propertyName))


