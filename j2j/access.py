"""Access elements."""

from copy import deepcopy

from .errors import Errors


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
        self.params = {
            'all_items_mode_used': False,
            'err_flag': False,
            'use_from_base': False,
        }

    def __touchnextdictelem(self, output_elem, pparts, pidx, set_val, new_val):
        """
        Get/Set elem to corresponding path.

        For eg:- This will convert `a.b.c` to {'a': {'b': 'c'}}.

        Input Params:
        output_elem: Elem I am working with
        pparts:  All the parts of path
        pidx:    For which path index I am working for
        set_val:  If set_val is true, I am here to write
        new_val:  Value I wish to set if set_val is true

        Output Params (in form of a tuple):
        output_elem: What is state of my new elem
        retval:  my return value, I will get this if I am at end of path
        need_to_exit: If true I need to exit from my parent path
        """
        if not isinstance(output_elem, dict):
            if self.params['all_items_mode_used']:
                self.params['err_flag'] = True
                return (None, None, True)
            assert False, "Trying for dict when list elem is found"

        nppart, need_to_exit = pparts[pidx], False
        try:
            # Check if we are not in at last part
            if pidx != (len(pparts) - 1):
                if set_val and (nppart not in output_elem):
                    # Checking the next element, for us to know that the
                    # new path(to be created) will be a dict or a list.
                    nxtpart = pparts[pidx + 1]
                    if (self.end_of_array in nxtpart) or \
                            (self.array_split in nxtpart):  # Array.
                        output_elem[nppart] = []
                    else:  # else dict.
                        output_elem[nppart] = {}
                # Move to next step, ie `b` in case of `a.b.c`.
                output_elem, retval = output_elem[nppart], None
            else:
                # We are in last part of path and it is a dict.
                # Why dict? Because it has been already deduced from
                # above `if`
                need_to_exit = True
                if set_val:
                    if nppart not in output_elem:
                        # Create that element and set new val
                        output_elem[nppart] = None
                    output_elem[nppart], retval = new_val, output_elem[nppart]
                else:
                    # dict, not last part and read only case
                    retval = output_elem[nppart]
            return (output_elem, retval, need_to_exit)
        except KeyError:
            # Exception, when `rules` contain a key not present in input.
            need_to_exit = True
            if self.params['all_items_mode_used']:
                self.params['err_flag'] = True
                return (None, None, need_to_exit)
            raise KeyError()
            return (output_elem, None, need_to_exit)

    def __touchnextarrelem(self, output_elem, numpparts, _pidx, set_val,
                           new_val, lastpart):
        """
        Get/Set elem to corresponding path.

        Just to be called from __touchelem, as I might assume some stuff

        Input Params:
        output_elem:  Elem I am working with
        pparts:   All the parts of path
        pidx:     For which path index I am working for
        set_val:   If set_val is true, I am here to write
        new_val:   Value I wish to set if set_val is true
        lastpart: If its true its last part by dict

        Output Params in form of a tuple:
        output_elem: What is state of my new elem
        retval:  my return value, I will get this if I am at end of path
        need_to_exit: If true I need to exit from my parent path
        """
        if not isinstance(output_elem, list):
            if self.params['all_items_mode_used']:
                self.params['err_flag'] = True
                return (None, None, True)
            assert False, "Trying for list when dict elem is found"

        _ppart = numpparts[_pidx]
        if _ppart != self.end_of_array:
            # That part must be valid integer
            ival = int(_ppart)
        else:
            # This is only for insert/for read you shldn't send #
            ival = len(output_elem)

        try:
            # lastpart means last after . and first part is for last part
            # after @ symbol
            if _pidx == (len(numpparts) - 1) and lastpart:
                if set_val:
                    if ival > (len(output_elem) - 1):
                        diff = ival - (len(output_elem) - 1)
                        for _ in range(diff):
                            output_elem.append(None)
                    (output_elem[ival], retval) = (new_val, output_elem[ival])
                else:
                    retval = output_elem[ival]
                return (output_elem, retval, True)
            else:
                # So its not the last part. So we have two possible cases
                # a.b@1.c or a.b@5@3
                if set_val and (ival > (len(output_elem) - 1)):
                    diff = len(output_elem) - 1 - ival
                    for _ in range(diff):
                        output_elem.append(None)
                output_elem, retval = output_elem[ival], None
                return (output_elem, retval, False)
        except IndexError:
            if self.params['all_items_mode_used']:
                self.params['err_flag'] = True
                return (None, None, True)
            raise IndexError()
            return (output_elem, None, True)

    def __touchallelem(self, output_elem, pparts, pidx, _pparts, _pidx,
                       set_val, new_val, copy_val):
            """Handle wildcard cases."""
            assert self.params['all_items_mode_used'] is False, \
                Errors.ALL_ITEMS_ERROR

            self.params['all_items_mode_used'] = True

            if isinstance(output_elem, dict):
                all_items = output_elem.keys()
            else:
                all_items = [str(i) for i in range(len(output_elem))]
            output_elemlist = []

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

                output_elem_i = self.__touchelem__(
                    output_elem, path_i, set_val, new_val, copy_val)

                if not self.params['err_flag']:
                    # I got an error lets skip
                    if (not self.params['use_from_base']) or \
                            (path_i2 == path_i):
                        output_elemlist.extend(output_elem_i)
                    else:
                        output_elem_i2 = self.__touchelem__(
                            output_elem, path_i2, set_val, new_val, copy_val)
                        output_elemlist.extend(output_elem_i2)
                else:
                    self.params['err_flag'] = False
            return output_elemlist

    def __touchelemwrapper__(self, json_elem, path, set_val=False,
                             new_val=None, copy_val=False,
                             use_from_base=False):
        """Function is wrapper arround __touchelem__()."""
        self.params['use_from_base'] = use_from_base
        return self.__touchelem__(json_elem, path, set_val, new_val, copy_val)

    def __touchelem__(self, json_elem, path, set_val, new_val, copy_val):
        """
        Get/Set elem to corresponding path.

        In favour of non repetition of code this code has become heavy.
        json_elem: json ds read
        path: The path about which I am talking
        set_val: If true I want to change value
        new_val: If set_val is true, this value is set. Just for clarification,
                for me Non is also a value
        copy_val: This will make deepcopy of return value if set to true

        Note:
        Currently path can have * only in case of set_val=False
        Don't call this fuction direcly
        """
        if path == self.root_elem:
            # If path equal to root_element, then return the same json_elem.
            assert not set_val, Errors.SET_ROOT_DIRECTLY
            return [json_elem]

        output_elem = json_elem

        # Lets split by dict separator
        pparts = path.split(self.dict_split)
        for pidx, ppart in enumerate(pparts):
            if str(ppart) == self.root_elem:
                assert pidx == 0, "Root elem in between doesn't make sense"
                continue

            if str(ppart) == self.all_items:
                return self.__touchallelem(
                    output_elem, pparts, pidx, [], -1, set_val, new_val,
                    copy_val)
            # for each part in dict separator
            if self.array_split not in ppart:
                # if no array split part ie pure dict
                (output_elem, retval, need_to_exit) = self.__touchnextdictelem(
                    output_elem, pparts, pidx, set_val, new_val)
                if need_to_exit:  # if true, means full traversal has been done
                    if retval is not None and copy_val:
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
                return self.__touchallelem(
                    output_elem, pparts, pidx, _pparts, 0, set_val, new_val,
                    copy_val)

            if len(_pparts[0]) != 0:
                (output_elem, retval, need_to_exit) = self.__touchnextdictelem(
                    output_elem, _pparts, 0, set_val, new_val)
                if need_to_exit:
                    if retval is not None and copy_val:
                        retval = deepcopy(retval)
                    return [retval]

            numpparts = _pparts[1:]
            lastpart = (pidx == (len(pparts) - 1))
            for _pidx, _ppart in enumerate(numpparts):
                if str(_ppart) == self.all_items:
                    return self.__touchallelem(
                        output_elem, pparts, pidx, numpparts, _pidx, set_val,
                        new_val, copy_val)
                (output_elem, retval, need_to_exit) = self.__touchnextarrelem(
                    output_elem, numpparts, _pidx, set_val, new_val, lastpart)
                if need_to_exit:
                    if retval is not None and copy_val:
                        retval = deepcopy(retval)
                    return [retval]

        print("To assert soon", output_elem)
        assert False, "SomeCases aren't handled"
        return [output_elem]

    def get_elem(self, json_elem, path):
        """Wrapper around."""
        return self.__touchelemwrapper__(json_elem, path)[0]

    def set_elem(self, json_elem, path, new_val):
        """Wrapper around set."""
        return self.__touchelemwrapper__(json_elem, path, True, new_val)[0]

    def get_list_of_paths(self, json_elem, path, use_from_base=False):
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
            json_elem, path, use_from_base=use_from_base)
