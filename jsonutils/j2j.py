"""This file converts json."""

from __future__ import print_function

import random
from copy import deepcopy


class JsonHelper(object):
    """This is my base class."""

    @staticmethod
    def guess_correct_key_for_dict(key, keyset=None):
        """Trying to guess correct datatype of my key."""
        if keyset is not None:
            if str(key) in keyset:
                return str(key)
        try:
            return int(key)
        except ValueError as _:
            try:
                return float(key)
            except ValueError as _:
                assert _
                return key


class AccessElementJson(object):
    """This class does whole magic of conversion."""

    def __init__(self, dict_split=".", array_split="@", root_elem="/",
                 end_of_array="$", all_items="*"):
        """
        Init some splitters for rulebook.

        dict_split  : Is splitter and next part is of dict
        array_split: Is splitter and next part tells array index
        root_elem  : Shows that path is root elem
        end_of_array: It is end of array, past last element
        all_items  : All possible cases of elements in array or dict
                    (Works on single layer only)
        """
        def checkparam(param):
            """Check the params for validity."""
            assert isinstance(param, str)
            assert len(param) == 1
            return str(param)

        self.dict_split = checkparam(dict_split)
        self.array_split = checkparam(array_split)
        self.root_elem = checkparam(root_elem)
        self.end_of_array = checkparam(end_of_array)
        self.all_items = checkparam(all_items)
        self.all_items_mode_used = {}
        self.err_flag = {}
        self.use_from_base = {}

    def __touchnextdictelem(self, outelem, pparts, pidx, setval, newval, rint):
        """
        Get/Set elem to corresponding path.

        Just to be called from __touchelem, as I might assume some stuff

        Input Params:
        outelem: Elem I am working with
        pparts:  All the parts of path
        pidx:    For which path index I am working for
        setval:  If setval is true, I am here to write
        newval:  Value I wish to set if setval is true
        rint:    Random int value to check if access all is set. If it is
                 set throwing error does not make sense. I will just set error
                 flag and return null

        Output Params (in form of a tuple):
        outelem: What is state of my new elem
        retval:  my return value, I will get this if I am at end of path
        need_to_exit: If true I need to exit from my parent path
        """
        if not isinstance(outelem, dict):
            if self.all_items_mode_used[rint]:
                self.err_flag[rint] = True
                return (None, None, True)
            assert False, "Trying for dict when list elem is found"

        ppart = pparts[pidx]
        nppart = JsonHelper.guess_correct_key_for_dict(ppart, outelem.keys())
        try:
            if pidx != (len(pparts) - 1):
                # Check if we are not in at last part
                if setval and (nppart not in outelem):
                    # We can create new path but we never know if its
                    # a dict or list so lets guess it, lets see next elem
                    nxtpart = pparts[pidx + 1]
                    if (self.end_of_array in nxtpart) or \
                            (self.array_split in nxtpart):
                        outelem[nppart] = []
                    else:
                        outelem[nppart] = {}

                # Move to next step
                outelem = outelem[nppart]
                return (outelem, None, False)
            else:
                # We are in last part of path and it is a dict
                if setval:
                    if nppart not in outelem:
                        # Create that element and set new val
                        outelem[nppart] = None
                    (outelem[nppart], retval) = \
                        (newval, outelem[nppart])
                else:
                    # dict, not last part and read only case
                    retval = outelem[nppart]
                return (outelem, retval, True)
        except KeyError as kerr:
            if self.all_items_mode_used[rint]:
                self.err_flag[rint] = True
                return (None, None, True)
            print(kerr)
            raise KeyError()
            return (outelem, None, True)

    def __touchnextarrelem(self, outelem, numpparts, _pidx, setval, newval,
                           lastpart, rint):
        """
        Get/Set elem to corresponding path.

        Just to be called from __touchelem, as I might assume some stuff

        Input Params:
        outelem:  Elem I am working with
        pparts:   All the parts of path
        pidx:     For which path index I am working for
        setval:   If setval is true, I am here to write
        newval:   Value I wish to set if setval is true
        lastpart: If its true its last part by dict
        rint:     Random int value to check if access all is set. If it is
                  set throwing error does not make sense. I will just set error
                  flag and return null

        Output Params in form of a tuple:
        outelem: What is state of my new elem
        retval:  my return value, I will get this if I am at end of path
        need_to_exit: If true I need to exit from my parent path
        """
        if not isinstance(outelem, list):
            if self.all_items_mode_used[rint]:
                self.err_flag[rint] = True
                return (None, None, True)
            assert False, "Trying for list when dict elem is found"

        _ppart = numpparts[_pidx]
        if _ppart != self.end_of_array:
            # That part nust be valid integer
            ival = int(_ppart)
        else:
            # This is only for insert/for read you shldn't send #
            ival = len(outelem)
        try:
            # lastpart means last after . and first part is for last part
            # after @ symbol
            if _pidx == (len(numpparts) - 1) and lastpart:
                if setval:
                    if ival > (len(outelem) - 1):
                        diff = ival - (len(outelem) - 1)
                        for _ in range(diff):
                            outelem.append(None)
                    (outelem[ival], retval) = (newval, outelem[ival])
                else:
                    retval = outelem[ival]
                return (outelem, retval, True)
            else:
                # So its not the last part. So we have two possible cases
                # a.b@1.c or a.b@5@3
                if setval and (ival > (len(outelem) - 1)):
                    diff = len(outelem) - 1 - ival
                    for _ in range(diff):
                        outelem.append(None)
                outelem = outelem[ival]
                return (outelem, None, False)
        except IndexError as ierr:
            if self.all_items_mode_used[rint]:
                self.err_flag[rint] = True
                return (None, None, True)
            print(ierr)
            raise IndexError()
            return (outelem, None, True)

    def __touchelemwrapper__(self, jsonelem, path, setval=False, newval=None,
                             copyval=False, use_from_base=False):
        """Function is wrapper arround __touchelem__()."""
        rint = random.randint(0, 1000000)
        self.all_items_mode_used[rint] = False
        self.err_flag[rint] = False
        self.use_from_base[rint] = use_from_base
        retval = self.__touchelem__(
            rint, jsonelem, path, setval, newval, copyval)
        self.all_items_mode_used.pop(rint)
        self.err_flag.pop(rint)
        self.use_from_base.pop(rint)
        return retval

    def __touchelem__(self, rint, jsonelem, path, setval, newval, copyval):
        """
        Get/Set elem to corresponding path.

        In favour of non repetition of code this code has become heavy.
        jsonelem: json ds read
        path: The path about which I am talking
        setval: If true I want to change value
        newval: If setval is true, this value is set. Just for clarification,
                for me Non is also a value
        copyval: This will make deepcopy of return value if set to true

        Note:
        Currently path can have * only in case of setval=False
        Don't call this fuction direcly
        """
        if path == self.root_elem:
            assert not setval, "You should set root direcly"
            return [jsonelem]

        def handleall_items(rint, outelem, pparts, pidx, _pparts, _pidx):
            """Handle wildcard cases."""
            assert self.all_items_mode_used[rint] is False, \
                "You can't use all_items mode multiple times"
            self.all_items_mode_used[rint] = True
            if isinstance(outelem, dict):
                all_items = outelem.keys()
            else:
                all_items = [str(i) for i in range(len(outelem))]
            outelemlist = []

            strpparts = u""
            if pidx < len(pparts) - 1:
                strpparts = self.dict_split.join(pparts[pidx + 1:])

            str_pparts = u""
            if (_pparts == []) or (pidx < len(_pparts) - 1):
                str_pparts = self.array_split.join(_pparts[_pidx + 1:])

            for iterall_items in all_items:
                if str_pparts != u"":
                    path_i = self.array_split + iterall_items + \
                        self.array_split + str_pparts
                    path_i2 = self.array_split + iterall_items
                else:
                    if _pparts == []:
                        # Its of form a.*.b or *
                        path_i = iterall_items
                        path_i2 = iterall_items
                    else:
                        # Its of form @* so str_pparts is null but
                        # we need to append @
                        path_i = self.array_split + iterall_items
                        path_i2 = self.array_split + iterall_items

                if strpparts != u"":
                    path_i = path_i + self.dict_split + strpparts

                outelem_i = self.__touchelem__(
                    rint, outelem, path_i, setval, newval, copyval)

                if not self.err_flag[rint]:
                    # I got an error lets skip
                    if (not self.use_from_base[rint]) or (path_i2 == path_i):
                        outelemlist.extend(outelem_i)
                    else:
                        outelem_i2 = self.__touchelem__(
                            rint, outelem, path_i2, setval, newval, copyval)
                        outelemlist.extend(outelem_i2)
                else:
                    self.err_flag[rint] = False
            return outelemlist

        # Now lets split by dict separator
        outelem = jsonelem
        pparts = path.split(self.dict_split)
        for pidx, ppart in enumerate(pparts):
            if str(ppart) == self.root_elem:
                assert pidx == 0, "Root elem in between doesn't make sense"
                continue

            if str(ppart) == self.all_items:
                return handleall_items(rint, outelem, pparts, pidx, [], -1)
            # for each part in dict separator
            if self.array_split not in ppart:
                # if no array split part ie pure dict
                (outelem, retval, need_to_exit) = self.__touchnextdictelem(
                    outelem, pparts, pidx, setval, newval, rint)
                if need_to_exit:
                    if retval is not None and copyval:
                        retval = deepcopy(retval)
                    return [retval]
                else:
                    continue
            # If I am here this means the part has array element.
            # the format will be aa@3 or aa@3 or @5 or /@4
            _pparts = ppart.split(self.array_split)
            if str(_pparts[0]) == self.root_elem:
                assert pidx == 0, "Root elem in between doesn't make sense"

            if str(_pparts[0]) == self.all_items:
                return handleall_items(rint, outelem, pparts, pidx, _pparts, 0)

            if len(_pparts[0]) != 0:
                (outelem, retval, need_to_exit) = self.__touchnextdictelem(
                    outelem, _pparts, 0, setval, newval, rint)
                if need_to_exit:
                    if retval is not None and copyval:
                        retval = deepcopy(retval)
                    return [retval]

            numpparts = _pparts[1:]
            lastpart = (pidx == (len(pparts) - 1))
            for _pidx, _ppart in enumerate(numpparts):
                if str(_ppart) == self.all_items:
                    return handleall_items(
                        rint, outelem, pparts, pidx, numpparts, _pidx)

                (outelem, retval, need_to_exit) = self.__touchnextarrelem(
                    outelem, numpparts, _pidx, setval, newval, lastpart, rint)
                if need_to_exit:
                    if retval is not None and copyval:
                        retval = deepcopy(retval)
                    return [retval]

        print("To assert soon", outelem)
        assert False, "SomeCases aren't handled"
        return [outelem]

    def get_elem(self, jsonelem, path):
        """Wrapper around."""
        return self.__touchelemwrapper__(jsonelem, path)[0]

    def set_elem(self, jsonelem, path, newval):
        """Wrapper around set."""
        return self.__touchelemwrapper__(jsonelem, path, True, newval)[0]

    def testset_elem(self, jsonelem, path):
        """Just for testing don't use it."""
        return self.set_elem(jsonelem, path, newval="haha")

    def get_list_of_paths(self, jsonelem, path, use_from_base=False):
        """
        Now I will be getting list of paths.

        Now we need to return list of elements
        for path a.*.b and in [ a.0, a.1, a.2, a.3, a.4 ]
        b only exits in 0 and 3
        if use_from_base = True:
            return a.0 and a.3 and b is condition to exist
        else:
            return a.0.b and a.3.b and b is condition to exist
        """
        return self.__touchelemwrapper__(
            jsonelem, path, use_from_base=use_from_base)


class ConvertJson(object):
    """"I am now trying to convert json."""

    def __init__(self):
        """Init."""
        self.access_elem_obj = AccessElementJson()

    def __implement_rules__(self, njson, ijson, rule):
        """Function has basic juice."""
        # This part is very generic and depends on use case.
        if njson is None:
            if rule["new_key_elem"] == self.access_elem_obj.root_elem:
                njson = []
            else:
                njson = {}
                self.access_elem_obj.set_elem(njson, rule["new_key_elem"], [])
        else:
            if rule["new_key_elem"] != self.access_elem_obj.root_elem:
                self.access_elem_obj.set_elem(njson, rule["new_key_elem"], [])
            else:
                njson = []
        data_arr = self.access_elem_obj.get_elem(njson, rule["new_key_elem"])
        elems = self.access_elem_obj.get_list_of_paths(ijson,
                                                       rule["base_elem"])
        for elem in elems:
            temp = {}
            for (key, val) in rule["changes"].items():
                if isinstance(val, list):
                    fval = []
                    for _val in val:
                        fval.append(self.access_elem_obj.get_elem(elem, _val))
                else:
                    fval = self.access_elem_obj.get_elem(elem, val)
                # this will make a.b work
                self.access_elem_obj.set_elem(temp, key, fval)
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
        errstr = "The format of rule is incorrect"
        assert isinstance(rjson, dict), errstr
        assert JsonHelper.guess_correct_key_for_dict("rules", rjson.keys()) \
            in rjson, errstr

        rules = rjson["rules"]  # fetching the rules.
        njson = None
        for _iter, rule in enumerate(rules):
            if _iter == 0:
                if rule["keep_others"]:
                    njson = deepcopy(ijson)
                else:
                    njson = None
            njson = self.__implement_rules__(njson, ijson, rule)
            # if not last element
            if rule["make_base"] and (_iter != (len(rules) - 1)):
                ijson = deepcopy(njson)
        return njson

c = ConvertJson()

ijson = {
    "menu": {
        "id": "file",
        "popup": {
            "menuitem": [
                {
                    "onclick": "CreateNewDoc()",
                    "value": "New",
                    "gravity": 1
                },
                {
                    "onclick": "OpenDoc()",
                    "value": "Open",
                    "gravity": 3
                },
                {
                    "onclick": "CloseDoc()",
                    "value": "Close",
                    "gravity": 4
                },
                {
                    "onclick": "SaveDoc()",
                    "value": "Save",
                    "gravity": 1.5
                }
            ]
        },
        "value": "File"
    }
}

rjson = {
    "rules": [
        {
            "base_elem": "menu.popup.menuitem@*",
            "changes": {
                "clickitem": "onclick",
                "data.value": ["value", "gravity"]
            },
            "keep_others": "True",
            "make_base": "True",
            "new_key_elem": "/"
        }
    ]
}

print(c.convert(ijson, rjson))
