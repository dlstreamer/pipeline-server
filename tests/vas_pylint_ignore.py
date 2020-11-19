'''
* Copyright (C) 2019-2020 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''

#Temp resolution (internal only)
#https://github.com/PyCQA/pylint/issues/2686

from pylint.utils import utils

class VASPylintIgnore:
    def __init__(self, *paths):
        self.paths = paths
        self.original_expand_modules = utils.expand_modules
        utils.expand_modules = self.patched_expand
        print("IGNORING PATHS: {ignored}".format(ignored=paths))

    def patched_expand(self, *args, **kwargs):
        result, errors = self.original_expand_modules(*args, **kwargs)

        def keep_item(item):
            if any(1 for path in self.paths if item['path'].startswith(path)):
                print("IGNORING {path}".format(path=item))
                return False
            print("KEEPING {path}".format(path=item))
            return True
        result = list(filter(keep_item, result))
        return result, errors
