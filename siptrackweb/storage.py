from django.core.files.storage import Storage

from pymongo import MongoClient
import gridfs


class GridFSStorage(Storage):
    pass