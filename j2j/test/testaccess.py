"""File to test accesselement.py."""

import json
from .testbase import TestBase
from j2j.access import AccessElementJson


class TestAccess(TestBase):
    """Time to test."""

    def __readjson__(self, fname):
        """Reading Json."""
        return self.__read__("samplejson", fname)

    def test0001(self, accessj):
        """Test01."""
        fle01 = self.__readjson__("sample0001.json")
        self.__equals__(accessj.get_elem(fle01, "/"), fle01)
        print ("Case1 Passed")
        self.__equals__(accessj.get_elem(fle01, "k3"), fle01["k3"])
        print ("Case2 Passed")
        self.__equals__(accessj.get_elem(fle01, "k4"), fle01["k4"])
        print ("Case3 Passed")
        self.__equals__(accessj.get_elem(fle01, "k4@4"), fle01["k4"][4])
        print ("Case4 Passed")
        print (accessj.get_list_of_paths(fle01, "*"))

    def test0002(self, accessj):
        """Test02."""
        fle02 = self.__readjson__("sample0002.json")
        self.__equals__(accessj.get_elem(fle02, "/"), fle02)
        print ("Case1 Passed")
        self.__equals__(accessj.get_elem(fle02, "@1"), fle02[1])
        print ("Case2 Passed")
        self.__equals__(accessj.get_elem(fle02, "@2"), fle02[2])
        print ("Case3 Passed")
        self.__equals__(accessj.get_list_of_paths(fle02, "@*"), fle02)
        print ("Case4 Passed")

    def test0003(self, accessj):
        """Test03."""
        fle03 = self.__readjson__("sample0003.json")
        json_a1 = accessj.get_list_of_paths(fle03, "*.high")
        json_a2 = accessj.get_list_of_paths(fle03, "*.high", use_from_base=True)
        json_b1 = json.loads('["now1", "now2"]')
        self.__equals__(json_a1, json_b1)
        print ("Case1 Passed")
        json_b2 = json.loads('[{"high": "now1"}, {"high": "now2"}]')
        self.__equals__(json_a2, json_b2)
        print ("Case2 Passed")

    def test0011(self, accessj):
        """Test11."""
        fle11 = self.__readjson__("sample0011.json")
        self.__equals__(accessj.get_elem(fle11, "/"), fle11)
        print ("Case1 Passed")
        # Get doesn't change anything
        self.__equals__(accessj.get_elem(fle11, "/"), fle11)
        print ("Case2 Passed")
        self.__checkassert__(
            AssertionError, "You should set root direcly", accessj.testset_elem,
            fle11, "/")
        print ("Case3 Passed")
        # Get doesn't change anything
        self.__equals__(accessj.get_elem(fle11, "/"), fle11)
        print ("Case4 Passed")
        self.__equals__(accessj.get_elem(fle11, "glossary"), fle11["glossary"])
        print ("Case5 Passed")
        self.__equals__(accessj.get_elem(fle11, "glossary.GlossDiv.GlossList"),
                        fle11["glossary"]["GlossDiv"]["GlossList"])
        print ("Case6 Passed")
        # get doesn't change anything
        self.__equals__(accessj.get_elem(fle11, "glossary.GlossDiv.GlossList"),
                        fle11["glossary"]["GlossDiv"]["GlossList"])
        print ("Case7 Passed")
        accessj.testset_elem(fle11, "glossary.GlossDiv.GlossList")
        self.__equals__("haha", fle11["glossary"]["GlossDiv"]["GlossList"])
        print ("Case8 Passed")
        self.__equals__(accessj.get_elem(fle11, "glossary"), fle11["glossary"])
        print ("Case9 Passed")
        accessj.testset_elem(fle11, "blabla")
        self.__equals__("haha", fle11["blabla"])
        print ("Case10 Passed")

    def test0015(self, cvrt):
        """Test15."""
        fle15 = self.__readjson__("sample0015.json")
        self.__equals__(
            cvrt.get_elem(fle15, "menu.items@0"), fle15["menu"]["items"][0])
        print ("Case1 Passed")
        oldval = cvrt.get_elem(fle15, "menu.items@0.id")
        self.__equals__(
            oldval, fle15["menu"]["items"][0]["id"])
        print ("Case2 Passed")
        self.__equals__(
            oldval, cvrt.testset_elem(fle15, "menu.items@0.id"))
        print ("Case3 Passed")
        self.__equals__(
            cvrt.get_elem(fle15, "menu.items@0.id"),
            "haha")
        print ("Case4 Passed")
        cvrt.testset_elem(fle15, "menu.items@0")
        self.__equals__(
            fle15["menu"]["items"][0],
            cvrt.get_elem(fle15, "menu.items@0"))
        print ("Case5 Passed")
        orglen = len(cvrt.get_elem(fle15, "menu.items"))
        cvrt.set_elem(fle15, "menu.items@$", "last")
        self.__equals__(
            len(cvrt.get_elem(fle15, "menu.items")),
            orglen + 1)
        print ("Case6 Passed")
    # print(t.testset_elem(f5, "menu.items@0"))
    # print(t.get_elem(f5, "menu.items"))
    # print(t.testset_elem(f5, "menu1.items"))
    # print(t.get_elem(f5, "/"))

if __name__ == '__main__':
    TCVTR = TestAccess()
    ACCESS_J = AccessElementJson()
    TCVTR.test0001(ACCESS_J)
    print ("*********")
    TCVTR.test0002(ACCESS_J)
    print ("*********")
    TCVTR.test0003(ACCESS_J)
    print ("*********")
    TCVTR.test0011(ACCESS_J)
    print ("*********")
    TCVTR.test0015(ACCESS_J)
