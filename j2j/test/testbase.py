"""File of testbase.py."""

import json
import os


class TestBase(object):
    """Time to test."""

    def __init__(self):
        """Constructor."""
        pass

    @classmethod
    def __read__(cls, directory, fname):
        """Read my json."""
        mylocation = os.path.dirname(
            os.path.realpath(__file__))
        dirpath = os.path.join(mylocation, directory)
        with open(os.path.join(dirpath, fname)) as data_file:
            jsonfile = json.load(data_file)
        return jsonfile

    @classmethod
    def __equals__(cls, json1, json2):
        """Check if two json are equal."""
        # print "json1", json1
        # print "json2", json2
        # print "__", "+++"
        assert json1 == json2, "There is a problem"

    @classmethod
    def __nequals__(cls, json1, json2):
        """Check if two json are equal."""
        # print "json1", json1
        # print "json2", json2
        # print "__", "+++"
        assert json1 != json2, "There is a problem"

    @classmethod
    def __checkassert__(
            cls, asserttype, assertmessage, func, *kargs, **vargs):
        """Check if we get an assert."""
        try:
            func(*kargs, **vargs)
            assert False, "Expected a failure"
        except Exception as exep:
            assert isinstance(exep, asserttype) and \
                assertmessage == exep.message
