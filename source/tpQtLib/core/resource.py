#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that defines a base class to load resources
"""

from __future__ import print_function, division, absolute_import

import os

from tpQtLib.Qt.QtGui import *

from tpPyUtils import folder
from tpQtLib.core import qtutils, pixmap as pixmap_resource
from tpPyUtils import path


class Resource(object):

    RESOURCES_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'resources')

    def __init__(self, *args):
        dirname = ''
        if args:
            dirname = os.path.join(*args)
        if os.path.isfile(dirname):
            dirname = os.path.dirname(dirname)
        self._dirname = dirname or self.RESOURCES_FOLDER

    @classmethod
    def generate_resources_file(cls, generate_qr_file=True, resources_folder=None):
        """
        Loop through resources adn generates a QR file with all of them
        :param generate_qr_file: bool, True if you want to generate the QR file
        :param resources_folder: str, Optional path where resources folder is located
        """

        res_file_name = 'res'

        if resources_folder is None or not os.path.isdir(resources_folder):
            resources_folder = cls.RESOURCES_FOLDER

        res_out_folder = resources_folder
        if not os.path.exists(resources_folder):
            raise RuntimeError('Resources folder {0} does not exists!'.format(resources_folder))

        res_folders = folder.get_sub_folders(resources_folder)
        res_folders = [os.path.join(resources_folder, x) for x in res_folders]
        res_folders = [x for x in res_folders if os.path.exists(x)]

        qrc_file = os.path.join(resources_folder, res_file_name + '.qrc')
        qrc_py_file = os.path.join(res_out_folder, res_file_name + '.py')

        if generate_qr_file:
            qtutils.create_qrc_file(res_folders, qrc_file)
        if not os.path.isfile(qrc_file):
            return

        qtutils.create_python_qrc_file(qrc_file, qrc_py_file)

    @classmethod
    def get(cls, *args):
        """
        Returns path for the given resource name
        :param args: str, name of the source to retrieve path of
        :return: str
        """

        return cls()._get(*args)

    @classmethod
    def icon(cls, *args, **kwargs):
        """
        Returns icon for the given resource name
        :param name: str, name of the icon
        :param extension: str, extension of the icon
        :param color: QColor, color of the icon
        :return: QIcon
        """

        return cls()._icon(*args, **kwargs)

    @classmethod
    def pixmap(cls, *args, **kwargs):
        """
        Returns QPixmap for the given resource name
        :param name: str, name of the pixmap
        :param category: str, category of the pixmap
        :param extension: str, extension of the pixmap
        :param color: QColor, color of the pixmap
        :return: QPixmap
        """

        return cls()._pixmap(*args, **kwargs)

    @classmethod
    def gui(cls, *args, **kwargs):
        """
        Returns QWidget loaded from .ui file
        :param name: str, name of the UI file
        :return:
        """

        return cls()._ui(*args, **kwargs)

    def dirname(self):
        """
        Returns absolute path to the resource
        :return: str
        """

        return self._dirname

    def _get(self, *args):
        """
        Returns the resource path with the given paths
        :param args: str, resource name
        :return: str
        """

        return path.clean_path(os.path.join(self.dirname(), *args))

    def _icon(self, name, extension='png', color=None):
        """
        Returns a QIcon object from the given resource name
        :param name: str, name of the icon
        :param extension: str, extension of the icon
        :param color: QColor, color of the icon
        :return: QIcon
        """

        p = self._pixmap(name=name, category='icons', extension=extension, color=color)
        return QIcon(p)

    def _pixmap(self, name, category='images', extension='png', color=None):
        """
        Return a QPixmap object from the given resource anme
        :param name: str, name of the pixmap
        :param category: str, category of the pixmap
        :param extension: str, extension of the pixmap
        :param color: QColor, color of the pixmap
        :return: QPixmap
        """

        path = self._get(category, name + '.' + extension)
        p = pixmap_resource.Pixmap(path)
        if color:
            p.set_color(new_color=color)

        return p

    def _ui(self, name):
        """
        Returns a QWidget loaded from .ui file
        :param name: str, name of the ui file you want to load
        :return: QWidget
        """

        return qtutils.ui_loader(ui_file=self.get('uis', name + '.ui'))
