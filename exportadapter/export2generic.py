# -*- coding: utf-8 -*-
from datetime import datetime
import os
from abc import ABCMeta, abstractmethod


class Export2Generic(object):
    """Generic class for exports to files"""
    __metaclass__ = ABCMeta
    
    _output_directory = None
    """target directory where the exports are saved"""
    timestamp_included = True
    """if true, the current timestamp will be included at the end of the filename"""

    def __init__(self, output_directory: str=None) -> None:
        """
        :param output_directory: defaults to the current directory if omitted.
        """
        if output_directory:
            self.output_directory = output_directory
        else:
            self.output_directory = os.getcwd()

    @staticmethod
    def _clean_path(path: str) -> str:
        """convert backslashes to slashes and strip any trailing slashes"""
        path = path.replace('\\', '/')
        return path.strip('/') if not path.endswith(':/') else path

    @staticmethod
    def _get_timestamp_string() -> str:
        return str(datetime.now())[0:19].replace('-', '').replace(' ', '_').replace(':', '')

    @property
    def output_directory(self) -> str:
        return self._output_directory

    @output_directory.setter
    def output_directory(self, output_directory: str) -> None:
        self._output_directory = self._clean_path(output_directory)
   
    @abstractmethod
    def export(self, result, file_name: str="pythonexport.exp", result_title: str='table'):
        pass
