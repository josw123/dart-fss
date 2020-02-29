# -*- coding: utf-8 -*-
import re
import os
import zipfile
import xmltodict
from collections import OrderedDict

from typing import List


def xml_to_dict(path: str, encoding: str = 'utf8') -> OrderedDict:
    """ Xml File to OrderedDict

    Parameters
    ----------
    path: str
        xml file path
    encoding: str
        file encoding

    Returns
    -------
    OrderedDict
        dictionary
    """
    with open(path, encoding=encoding) as f:
        res = xmltodict.parse(f.read())
    return res


def unzip(file: str, path: str = None, newFolder: bool = True) -> str:
    """ unzip method

    Parameters
    ----------
    file: str
        zip 파일
    path: str
        unzip 경로
    newFolder: bool
        폴더 생성여부

    Returns
    -------
    str
        unzip 경로
    """
    os.path.altsep = '\\'  # fixed extract bug
    # Split the path into a pair head and tail
    head, tail = os.path.split(file)

    if path:
        extract_path = path
    else:
        extract_path = head

    with zipfile.ZipFile(file, 'r') as zip_ref:
        if newFolder:
            new_folder = tail.replace('.zip', '')
            extract_path = os.path.join(extract_path, new_folder)
        zip_ref.extractall(path=extract_path)
    return extract_path


def search_file(path: str, filename: str = None, extensions: str = 'xbrl') -> List[str]:
    """ File 검색

    Parameters
    ----------
    path: str
        파일 검색 위치
    filename: str
        파일명
    extensions: str
        파일 확장자

    Returns
    -------
    list of str
        검색된 파일 리스트
    """
    file_list = []
    for root, _, files in os.walk(path):
        for file in files:
            if filename is not None and re.search(filename, file):
                file_list.append(os.path.join(root, file))
            if file.endswith('.' + extensions):
                file_list.append(os.path.join(root, file))
    return file_list


def create_folder(path: str):
    """ 폴더생성

    Parameters
    ----------
    path: str
        폴더 생성

    """
    import pathlib
    try:
        pathlib.Path(path).mkdir(parents=True, exist_ok=True)
    except FileExistsError:
        pass
    except OSError:
        raise


def get_cache_folder():
    """ Create cache folder

    Returns
    -------
    str
        Cache Folder Path
    """
    from appdirs import user_cache_dir
    appname = 'dart-fss'
    cache_dir = user_cache_dir(appname)
    create_folder(cache_dir)
    return cache_dir
