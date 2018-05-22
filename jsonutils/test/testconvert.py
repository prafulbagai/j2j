"""File to test convert.py."""

import json

from jsonutils.test.testbase import TestBase
from jsonutils import AccessElementJson
from jsonutils import ConvertJson


class TestConvert(TestBase):
    """Time to test."""

    def __readjson__(self, fname):
        """Reading Json."""
        return self.__read__("samplejson", fname)

    def __readrule__(self, fname):
        """Reading Rules."""
        return self.__read__("samplerules", fname)

    def test0001(self, cvrt):
        """Test01."""
        fle01 = self.__readjson__("sample0001.json")
        rule01 = self.__readrule__("rule0001_sample0001.json")
        data = cvrt.convert(fle01, rule01)
        ideal = json.loads('[{"newk1": "v1", "check": ["v3"], "newk4": "v41", \
            "newk5": {"inner": "v5"}}]')
        self.__equals__(data, ideal)

    def test0004(self, cvrt):
        """Test04."""
        fle04 = self.__readjson__("sample0004.json")
        rule01 = self.__readrule__("rule0001_sample0004.json")
        data = cvrt.convert(fle04, rule01)
        ideal = json.loads('[{"clickitem": "CreateNewDoc()", "data": \
            {"value": ["New", 1]}}, {"clickitem": "OpenDoc()", "data": \
            {"value": ["Open", 3]}}, {"clickitem": "CloseDoc()", "data": \
            {"value": ["Close", 4]}}, {"clickitem": "SaveDoc()", "data": \
            {"value": ["Save", 1.5]}}]')
        self.__equals__(data, ideal)

if __name__ == '__main__':
    TCVTR = TestConvert()
    ACCESS_J = AccessElementJson()
    CVR_J = ConvertJson(ACCESS_J)
    TCVTR.test0001(CVR_J)
    print "Case1 Passed"
    TCVTR.test0004(CVR_J)
    print "Case2 Passed"
