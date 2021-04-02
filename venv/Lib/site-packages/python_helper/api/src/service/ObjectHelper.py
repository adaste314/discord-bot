from python_helper.api.src.domain import Constant
from python_helper.api.src.service import StringHelper

def equal(responseAsDict,expectedResponseAsDict) :
    filteredResponse = StringHelper.filterJson(str(responseAsDict))
    filteredExpectedResponse = StringHelper.filterJson(str(expectedResponseAsDict))
    return filteredResponse == filteredExpectedResponse

def filterIgnoreKeyList(objectAsDictionary,ignoreKeyList):
    if objectAsDictionary and ignoreKeyList :
        filteredObjectAsDict = {}
        for key in sorted(objectAsDictionary):
            if key not in ignoreKeyList :
                if objectAsDictionary[key].__class__.__name__ == Constant.DICT :
                    objectAsDictionary[key] = filterIgnoreKeyList(objectAsDictionary[key],ignoreKeyList)
                filteredObjectAsDict[key] = objectAsDictionary[key]
        return filteredObjectAsDict
    return objectAsDictionary
