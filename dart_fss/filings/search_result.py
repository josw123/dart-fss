# -*- coding: utf-8 -*-
from typing import Dict

from dart_fss.utils import dict_to_html
from dart_fss.filings.reports import Report


class SearchResults(object):
    """ DART 검색결과 정보를 저장하는 클래스"""

    def __init__(self, resp):
        self._page_no = resp['page_no']
        self._page_count = resp['page_count']
        self._total_count = resp['total_count']
        self._total_page = resp['total_page']
        self._report_list = [Report(**x) for x in resp['list']]

    @property
    def page_no(self):
        """ 표시된 페이지 번호 """
        return self._page_no

    @property
    def page_count(self):
        """페이지당 표시할 리포트수"""
        return self._page_count

    @property
    def total_count(self):
        """int: 총 건수"""
        return self._total_count

    @property
    def total_page(self):
        """int: 총 페이지수"""
        return self._total_page

    @property
    def report_list(self):
        """list of Report: 검색된 리포트 리스트"""
        return self._report_list

    def to_dict(self) -> Dict:
        """ dict 타입으로 반환

        Returns
        -------
        dict of str
            검색 결과 dict 타입로 반환

        """
        return {
            'page_no': self.page_no,
            'page_count': self.page_count,
            'total_count': self.total_count,
            'total_page': self.total_page,
            'report_list': [x.to_dict() for x in self.report_list]
        }

    def pop(self, index=-1):
        """ 주어진 index 의 리포트를 반환하며, 리스트에서 삭제하는 함수"""
        return self._report_list.pop(index)

    def __repr__(self):
        from pprint import pformat
        return pformat(self.to_dict())

    def _repr_html_(self):
        return dict_to_html(self.to_dict(), exclude=['pages'], header=['Label', 'Data'])

    def __getitem__(self, item):
        return self._report_list[item]

    def __len__(self):
        return len(self._report_list)