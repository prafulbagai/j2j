"""This file converts json."""

from __future__ import print_function

from copy import deepcopy

from .errors import Errors
from .access import AccessElementJson


class ConvertJson(object):
    """"I am now trying to convert json."""

    def __init__(self):
        """Init."""
        self.access_elem_obj = AccessElementJson()

    def __implement_rules__(self, njson, ijson, rule):
        """Function has basic juice."""
        # This part is very generic and depends on use case.

        new_key_elem = rule.get('new_key_elem')
        if not new_key_elem:
            assert False, Errors.INCORRECT_RULE_FORMAT

        if new_key_elem == self.access_elem_obj.root_elem:
            # If `new_key_element` is same as root_element.
            njson = []
        else:
            # else set new_json from `new_key_elem`.
            self.access_elem_obj.set_elem(njson, new_key_elem, [])

        data_arr = self.access_elem_obj.get_elem(njson, new_key_elem)
        # fetching elements from the base_element provided.
        elems = self.access_elem_obj.get_list_of_paths(ijson,
                                                       rule["base_elem"])
        for elem in elems:
            temp = {}
            for (key, val) in rule["changes"].items():
                """
                Fetching the value of the element to be changed and setting it
                into temp.
                """
                if isinstance(val, list):
                    # Get value of each element presented in a list and
                    # append in the list.
                    fval = []
                    for _val in val:
                        fval.append(self.access_elem_obj.get_elem(elem, _val))
                else:
                    fval = self.access_elem_obj.get_elem(elem, val)

                # this will make a.b work(when in case of dict.)
                self.access_elem_obj.set_elem(temp, key, fval)
            # ####################
            # Understand how appending `temp` into `data_array` changes `njson`
            # ####################
            data_arr.append(temp)
        return njson

    def convert(self, ijson, rjson):
        """
        Convert json to new json.

        The rules format will be
        {
            "rules":[
            {           //rule1
            "base_elem":...,
            "keep_others":True/False,
            "make_base":True/False,
            "new_key_elem": "value it takes in oldelem"
            "changes":{
            ...,
            ...
            }
            },
            {          //rule2 This will be applied after rule1
            "base_elem":...,
            "new_key_elem": "value it takes in oldelem"
            "changes":{
            ...,
            ...
            }
            },
            ]
        }
        """
        assert isinstance(rjson, dict), Errors.INCORRECT_RULE_FORMAT

        rules = rjson.get("rules")  # fetching the rules.
        if not rules:
            assert False, Errors.INCORRECT_RULE_FORMAT

        njson = None
        for _iter, rule in enumerate(rules):
            if _iter == 0:
                if rule.get("keep_others"):
                    njson = deepcopy(ijson)
                else:
                    njson = {}

            # creating new json.
            njson = self.__implement_rules__(njson, ijson, rule)[0]
            # if not last element
            if rule.get("make_base") and (_iter != (len(rules) - 1)):
                ijson = deepcopy(njson)
        return njson
