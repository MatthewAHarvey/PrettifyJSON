import sys
import re

# Call this with PrettifyJSON.py filename everyN
# everyN decides where the linebreak occurs in an array section. Each line will have N comma separated entries

# fName = 'CH405_35_gun_90deg_SAS_190705_0850.json'
# with open(fName, 'r', encoding="utf-8") as JSONfile:
#   data = JSONfile.read()

def fixDuplicateEndingLabVIEWBug(data):
    """Given an input JSON string, strips the duplicated fragment that a LabVIEW bug is adding to the end of our save files."""
    duplicateString = '''g":[
    ]
}g":[
    ]
}'''
    if(data[-len(duplicateString):] == duplicateString):
        data = data[:-12]
    return data
    

def roundDecimalPlaces(data, maxDP=-1):
    """Given an input JSON string, truncates floating point numbers to a maximum number of decimal places, maxDP."""
    floatMatches = list(re.finditer('\d+\.\d+', data))
    dataList = []
    prevEndIndex = 0
    for floatMatch in floatMatches:
        floatStartI = floatMatch.span()[0]
        floatEndI = floatMatch.span()[1]
        floatStr = data[floatStartI:floatEndI]
        if(maxDP == -1):
            floatStr = str(float(floatStr))
        else:
            floatStr = str(round(float(floatStr) * 10**maxDP) / 10**maxDP)
        dataList.append(data[prevEndIndex:floatStartI])
        dataList.append(floatStr)
        prevEndIndex = floatEndI
    # add remaining data after last float
    lastFloatEndIndex = floatMatches[-1].span()[1]
    dataList.append(data[lastFloatEndIndex:])
    # make in to string
    return ''.join(dataList)

def getArrayPositions(data):
    """Given a JSON string, returns a list of the indices of the start [ and end ] list brackets."""
    bracketMatches = list(re.finditer('\\[|\\]', data))
    openIndices = []
    arrayIndices = []
    for match in bracketMatches:
        bracketIndex = match.span()[0]
        bracket = data[bracketIndex]
        if(bracket == '['):
            openIndices.append(bracketIndex)
        else:
            latestOpenBracketIndex = openIndices.pop()
            arrayIndices.append([latestOpenBracketIndex, bracketIndex])
    return arrayIndices

def getNumericArrayPositions(data):
    """Given a JSON string, returns a list of the start and end indices of numeric type lists."""
    arrayIndices = getArrayPositions(data)
    numericArrayIndices = []
    for array in arrayIndices:
        strToList = eval(data[array[0]:array[1]+1])
        if len(strToList) > 0:
            typeOfListEntry = type(strToList[0])
            if typeOfListEntry != list:
                numericArrayIndices.append(array)
    return numericArrayIndices

def reformatArrays(data, everyN = 20):
    """Given a JSON string, reformats arrays so that they are more readable. Instead of one entry per line, multiple entries are displayed per line with a newline added everyN lines."""
    numericListIndices = getNumericArrayPositions(data)
    newlinesToRemove = []
    for indices in numericListIndices:
        start, end = indices
        # find the commas followed by newlines
        arrayNewlines = list(re.finditer(',\\n +', data[start: end]))
        del arrayNewlines[everyN-1::everyN] # keep these ones!
        # get the indices of where these are in the data file
        for newline in arrayNewlines:
            commaStart = start + newline.span()[0]
            commaEnd = start + newline.span()[1]
            newlinesToRemove.append((commaStart, commaEnd))
    # add all data before first array
    dataList = []
    dataList.append(data[0:newlinesToRemove[0][0]])
    for i in range(len(newlinesToRemove) - 1):
        # add a comma
        dataList.append(', ')
        # now append the normal data up to the next comma
        startI = newlinesToRemove[i][1]
        stopI = newlinesToRemove[i+1][0]
        dataList.append(data[startI:stopI])
    # add remaining data after last array
    dataList.append(', ')
    dataList.append(data[newlinesToRemove[-1][1]:])
    # make in to string
    return ''.join(dataList)

def main(argList):
    # expects:
    # filename, number of decimal places, number of columns in an array
    nArgs = len(argList)
    if(nArgs == 2):
        fName = argList[1]
        maxDP = 3
        everyN = 20
    elif(nArgs == 3):
        fName = argList[1]
        maxDP = int(argList[2])
        everyN = 20
    elif(nArgs == 4):
        fName = argList[1]
        maxDP = int(argList[2])
        everyN = int(argList[3])
    else:
        print("Incorrect number of arguments")
        print("Usage: scriptName.py filename numberOfDecimalPlacesToTruncateFloatsTo numberOfColumnsPerLineOfArray")
        sys.exit(1)

    print(f"FileName: {fName}")
    print(f"Max Number of Decimals Places: {maxDP}")
    print(f"Max Array Entries Per Line: {everyN}")

    with open(fName, 'r', encoding="utf-8") as JSONfile:
        data = JSONfile.read()
    data = fixDuplicateEndingLabVIEWBug(data)
    excessFloatZeroesRemovedData = roundDecimalPlaces(data, maxDP)
    result = reformatArrays(excessFloatZeroesRemovedData, everyN)

    newFName = fName[:-5] +'_formatted.json'
    with open(newFName, 'w', encoding="utf-8") as JSONfile:
        JSONfile.write(result)
    sys.exit(0)

if __name__ == '__main__':
    main(sys.argv)