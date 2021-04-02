from python_helper.api.src.service import StringHelper, LogHelper
from python_helper.api.src.domain import Constant as c

def getFilteredSetting(setting,globals) :
    if c.STRING == setting.__class__.__name__ :
        return StringHelper.getFilteredString(setting,globals)
    return setting

def getSetting(nodeKey,settingTree) :
    try :
        return accessTree(nodeKey,settingTree)
    except Exception as exception :
        LogHelper.debug(getSetting,f'Not possible to get {nodeKey} node key. Cause: {str(exception)}')
        return None

def accessTree(nodeKey,tree) :
    if nodeKey == c.NOTHING :
        try :
            return StringHelper.filterString(tree)
        except :
            return tree
    else :
        nodeKeyList = nodeKey.split(c.DOT)
        lenNodeKeyList = len(nodeKeyList)
        if lenNodeKeyList > 0 and lenNodeKeyList == 1 :
             nextNodeKey = c.NOTHING
        else :
            nextNodeKey = c.DOT.join(nodeKeyList[1:])
        return accessTree(nextNodeKey,tree[nodeKeyList[0]])
