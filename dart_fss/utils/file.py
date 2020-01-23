# -*- coding: utf-8 -*-
import re
import os
import zipfile

from typing import List


def unzip(file: str, path: str = None, create_folder=True) -> str:
    """ unzip method

    Parameters
    ----------
    file: str
        zip 파일
    path: str
        unzip 경로
    create_folder: bool
        폴더 생성여부

    Returns
    -------
    str
        unzip 경로
    """
    os.path.altsep = '\\'  # fixed extract bug
    if path:
        extract_path = path
    else:
        extract_path = '\\'.join(file.split('\\')[:-1])

    with zipfile.ZipFile(file, 'r') as zip_ref:
        if create_folder:
            folder = file.split('\\')[-1]
            folder = folder.replace('.zip', '')
            extract_path = os.path.join(extract_path, folder)
        zip_ref.extractall(extract_path)
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
    files = []
    for root, _, files in os.walk(path):
        for file in files:
            if filename is not None and re.search(filename, file):
                files.append(os.path.join(root, file))
            if file.endswith('.' + extensions):
                files.append(os.path.join(root, file))
    return files


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

