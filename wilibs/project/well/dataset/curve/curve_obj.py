from .curveapi import *
from tempfile import TemporaryFile
import json


class Curve:
    def __init__(self, token, curveInfo):
        self.token = token
        self.curveInfo = {
            'idDataset': curveInfo['idDataset'],
            'idCurve': curveInfo['idCurve'],
            'name': curveInfo['name'],
            'description': curveInfo['description'],
            'tags': curveInfo['relatedTo']['tags'] if curveInfo["relatedTo"] is not None and "tags" in curveInfo[
                "relatedTo"] else []
        }
        self.curveId = curveInfo['idCurve']
        self.curveName = curveInfo['name']
        self.datasetId = curveInfo['idDataset']

    def __repr__(self):
        obj = dict(self.curveInfo)
        return str(obj)

    def __str__(self):
        return self.__repr__()

    def getCurveInfo(self):
        """Return curve meta data (info)
        """
        check, content = getCurveInfo(self.token, self.curveId)
        if check:
            return content
        return None

    def getCurveData(self):
        """Return object contain data of curve
        """
        check, content = getCurveData(self.token, self.curveId)
        if check:
            return content
        return None

    def updateCurveData(self, curveData, name=False):
        """Update data to curve by array of object

        Args:
            data: array of object like {'x':25, 'y':16} with y is index
            name: optional if you want to change curve name

        Returns:
            None if no error
            err as string to describe what err is

            curveData = [{'x':5, 'y':7}, {'x':8, 'y':8}]
            curve = app.getCurveById(78)
            err = curve.updateCurveData(curveData)
            if err:
                print(err)
        """
        tempFile = TemporaryFile('r+')
        tempArr = []
        for i in curveData:
            temp = [i['y'], i['x']]
            tempArr.append(temp)
        tempFile.write(str(json.dumps(tempArr)))
        tempFile.seek(0)
        return self.updateCurveDataByFile(tempFile, name)

    def updateCurveDataByFile(self, data, name=False):
        """Update data to curve by file .txt

        Args: 
            data: file object
            name (optional): name you want to change
        
        Returns:
            None if no error
            err as string to describe what err is

        Example:
            data.txt:
            [[1,2],[3,4],[5,6]]  

            #[1,2] mean {x:2, y:1}

            curve = app.getCurveById(78)
            file = open('data.txt', 'rb')
            err = curve.updateCurveDataByFile(file) // array 
            if err:
                print(err)

        """
        check, content = updateCurveData(self.token, self.curveInfo['idDataset'], self.curveInfo['idCurve'], data, name)
        if check:
            print("Update datacurve successful")
            return True
        else:
            print(content)
        return False

    def editCurveInfo(self, **data):
        """Edit curve info

        Args:
            name, duplicate, unit, initValue (**kwargs) (optional)
        
        Returns:
            None if edit success
            String describe err if false
        
        Example:
            err = curve.editCurveInfo(name = 'new name', unit = 'cm', initValue = '60', duplicate = 1)
            if err:
                print(err)

        """
        check, content = editCurveInfo(self.token, self.curveInfo['idCurve'], **data)
        if check:
            return True
        return False

    def deleteCurve(self):
        check, content = deleteCurve(self.token, self.curveId)
        if check:
            return True
        else:
            print(content)
        return False

    def clipDataCurve(self, minValue, maxValue):
        if minValue > maxValue:
            print("minValue and maxValue is not valid")
            return None
        check, curveData = getCurveData(self.token, self.curveId)
        if check:
            for raw in curveData:
                if raw['x'] is not None and raw['x'] < minValue:
                    raw['x'] = minValue
                elif raw['x'] is not None and raw['x'] > maxValue:
                    raw['x'] = maxValue
            content = self.updateCurveData(curveData)
            return content
        else:
            print("curve data not found")
        return None

    def copyFamily(self, sourceCurve):
        if not sourceCurve:
            print("sourceCurve not found")
            return False
        sourceCurveObj = sourceCurve.getCurveInfo()
        err = self.editCurveInfo(name=self.getCurveInfo()["name"], idFamily=sourceCurveObj["idFamily"])
        if err:
            print(err)
            return False
        else:
            return True

    def renameCurve(self, newName):
        err = self.editCurveInfo(name=newName)
        if err:
            print(err)
            return False
        else:
            return True

    def addTags(self, tags):
        curveInfo = self.getCurveInfo()
        relatedTo = curveInfo["relatedTo"]
        if relatedTo and "tags" in relatedTo:
            oldTags = relatedTo["tags"]
            newTags = oldTags
            for t in tags:
                if not (t in oldTags):
                    newTags = newTags + [t]
            relatedTo["tags"] = newTags
            self.curveInfo["tags"] = relatedTo["tags"]
        else:
            relatedTo = {
                "tags": tags
            }
        check = self.editCurveInfo(relatedTo=relatedTo, name=curveInfo["name"])
        return check

    def removeTags(self, tags):
        curveInfo = self.getCurveInfo()
        relatedTo = curveInfo["relatedTo"]
        if relatedTo and "tags" in relatedTo:
            for t in tags:
                if t in relatedTo["tags"]:
                    relatedTo["tags"].remove(t)
                    self.curveInfo["tags"] = relatedTo["tags"]
        check = self.editCurveInfo(relatedTo=relatedTo, name=curveInfo["name"])
        return check
