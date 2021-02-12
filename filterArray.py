import numpy as np
import re
import csv
import json
import datetime as dt
from collections import namedtuple


def csvToTuple(filePath):
    """Convert a csv file to a list of tuples"""
    with open(filePath, 'r') as f:
        reader = csv.reader(f)
        converted = [tuple(row) for row in reader]
        return converted


def findType(value):
    """Find the dtype corresponding to of a value.

        Args:
            value (string): The string for which the dtype will be evaluated.

        Returns:
            string: The dtype to use.
    """
    if type(value) == str:
        dateRegex = '([12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]))'
        dateVal = re.match(dateRegex, value)
        floatVal = re.match('^\d+\.\d*$', value)
        intVal = re.match('^\d+$', value)
        if dateVal:
            valueType = 'M8[D]'
        elif floatVal:
            valueType = 'f8'
        elif intVal:
            valueType = 'int'
        else:
            valueType = 'O'
    return valueType


def replaceNulls(valueTuple, numericList):
    """Replace null values by zeros in a list.

        Args:
            valueTuple (tuple): A tuple containing the list of values and indexes.
            numericList (list): list of numeric columns.

        Returns:
            list: The return value

    """
    for idx, val in enumerate(valueTuple):
        isNumeric = idx in numericList
        if len(val) == 0 and isNumeric:
            yield 0
        else:
            yield val


def getNumindexes(typeList):
    """Find the indexes of the numeric columns.

        Args:
            typeList (list): A list of numpy dTypes
            converted to strings.

        Returns:
            generator: the returned generator.

        """
    """Find the indexes of the numeric columns"""
    for index, curList in enumerate(typeList):
        if re.match("f8|int", curList[1]):
            yield index

def roundSum(col):
    """Calculate the sum for a column
        round it to two precision points

        Args:
            col (numpy Array): The values to sum.

        Returns:
            float: The rounded sum.

        """
    colSum = sum(col)
    return round(colSum, 2)


def toTimezone(dateObject):
    """Convert a datetime object to iso 8601 format.

        Args:
            dateObject: A datetime object.

        Returns:
            string: The oconverted value.

        """
    return dt.datetime.strftime(dateObject, '%Y-%m-%dT%H:%M:%S.%SZ')


def toTuples(array, cols):
    """Create name,column pairs for a dict.

        Args:
            array (numpy Array) : The Array to convert.
            cols (list): The array's column names.

        Returns:
            tuple: Name of the column and its values (numpy Array).

        """
    for name in cols:
        col = array[name]
        kind = col.dtype.kind
        if kind == "M":
            yield (name, [toTimezone(x) for x in col.tolist()])
        else:
            yield (name, col.tolist())


def sliceTime(array, start, end, col='Date'):
    """Slices a numpy Array based on specified dates.
    
        Args:
            array (numpy Array) : The Array to slice.
            start (datetime object) : The start date for the slicing
            end (datetime object) : The end date for the slicing
            col (string) : The column on which the slicing will be applied
    
        Returns:
            Numpy Array: The sliced array.
    
        """
    targetCol = array[col].tolist()
    matchValues = [idx if (val >= start) & (val <= end)
                   else False for idx, val in enumerate(targetCol)]
    mask = list(filter(lambda x: x, matchValues))
    return array[mask]


def arrayToDict(arr, arr_columns, start_Date, end_Date):
    """Generate two dicts for the periods before the provided timespan and
        and the current period.

        Args:
            arr (Numpy Array): The original Array.
            startDate (string): The start date of the current period.
            endDate (string): The end date of the current period.

        Returns:
            namedtuple: The filtered Arrays

        """
    startDate = dt.datetime.strptime(start_Date, '%Y-%m-%d')
    endDate = dt.datetime.strptime(end_Date, '%Y-%m-%d')
    delta = endDate - startDate
    previous_period_start = startDate - delta
    previous_period_array = sliceTime(arr, previous_period_start, startDate)
    current_period_array = sliceTime(arr, startDate, endDate)
    previous_dict = dict(list(toTuples(previous_period_array, arr_columns)))
    current_dict = dict(list(toTuples(current_period_array, arr_columns)))
    returnTuple = namedtuple(
        'filteredData', ['current_period', 'previous_period'])
    return returnTuple(current_dict, previous_dict)


def getPeriodSdum(valuesDict, metricList):
    """Calculate the sum for each column in a value dict.

        Args:
            valuesDict (dict): The dict for which the sums will be calculated.
            metricList (list): The list of metrics.

        Returns:
            dict: the sum for each metric.

        """
    sumDict = dict((name, roundSum(valuesDict[name])) for name in metricList)
    return sumDict


def makeJson(arr):
    returnVal = json.dumps(arr, encoding='utf-8')
    return returnVal


def generateValues(csvFilePath):
    dataList = csvToTuple(csvFilePath)
    # split the columns and the data
    columns = dataList[0]
    dataraw = dataList[1:]
    testRow = dataList[1]
    # Find the dtype of each column
    dtypes = [(col, findType(val)) for col, val in zip(columns, testRow)]
    # Generate a list containing the indexes of numeric columns
    floatList = list(getNumindexes(dtypes))
    # Remove the nulls from the data
    noNans = [tuple(replaceNulls(i, floatList)) for i in dataraw]
    # Create the final array
    data_Array = np.array(noNans, dtype=dtypes)
    returnTuple = namedtuple(
        'rawData', ['data', 'dtypes', 'floatList', 'columns'])
    return returnTuple(data_Array, dtypes, floatList, columns)


def dictList(value_dict, rowsCol='Date'):
    """Converts a dict to a list of dict,
       one dict for each row.

        Args:
            value_dict (dict): The dict to convert.
            rowsCol (string): The key that will be used
            to count the number of rows.

        Returns:
            list: The dict converted to a list of dicts.

    """
    columns = value_dict.keys()
    rowCount = range(len(value_dict[rowsCol]))
    converted = [dict((col, value_dict[col][x]) for col in columns)
                 for x in rowCount]
    return converted


def exportToJson(rawData, period_start, period_end,):
    # Convert the numpy Array and its values to a dict
    data_tuple = arrayToDict(
        rawData.data, rawData.columns, period_start, period_end)
    # Calculate the sums for the current and the previous period
    metric_indexes = np.array(rawData.dtypes)
    metrics = [row[0] for row in metric_indexes[rawData.floatList]]
    current_period = data_tuple.current_period
    previous_period = data_tuple.previous_period
    # Get the filtered data for the current and the previous period
    currentSumDict = getPeriodSdum(current_period, metrics)
    previousSumDict = getPeriodSdum(previous_period, metrics)
    # Calculate the sums for the current and the previous period
    # prepare the value to export them as a json file
    returnStr = makeJson({'data': dictList(current_period), 'currentSum': currentSumDict,
                          'beforeSum': previousSumDict, 'beforeData': dictList(previous_period)})
    return returnStr



