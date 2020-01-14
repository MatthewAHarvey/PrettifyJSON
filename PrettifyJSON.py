import sys
import re

# Call this with PrettifyJSON.py filename everyN
# everyN decides where the linebreak occurs in an array section. Each line will have N comma separated entries

# fName = 'CH405_35_gun_90deg_SAS_190705_0850.json'
# with open(fName, 'r', encoding="utf-8") as JSONfile:
#   data = JSONfile.read()

def fixDuplicateEndingLabVIEWBug(data):
    duplicateString = '''g":[
    ]
}g":[
    ]
}'''
    # print(data[-len(duplicateString):])
    if(data[-len(duplicateString):] == duplicateString):
        # print("DUPLICATE")
        # print(data[-12:])
        data = data[:-12]
    # print(data[-20:])
    return data
    

def roundDecimalPlaces(data, maxDP=-1):
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

def arrayPositions(data):
    bracketMatches = list(re.finditer('\\[|\\]', data))
    prevBracket = ''
    openBracketPositions = []
    openBracketDuplicates = []
    closeBracketPositions = []
    closeBracketDuplicates = []
    for match in bracketMatches:
        bracketIndex = match.span()[0]
        bracket = data[bracketIndex]
        if(bracket == '['):
            openBracketPositions.append(bracketIndex)
            if(bracket == prevBracket):
                openBracketDuplicates.append(len(openBracketPositions) - 1)
        else:
            closeBracketPositions.append(bracketIndex)
            if(bracket == prevBracket):
                closeBracketDuplicates.append(len(closeBracketPositions) - 1)
        prevBracket = bracket
    for i in reversed(openBracketDuplicates):
        del openBracketPositions[i]
    for i in reversed(closeBracketDuplicates):
        del closeBracketPositions[i]
    return openBracketPositions, closeBracketPositions    

def reformatArrays(data, everyN = 20):
    openBracketPositions, closeBracketPositions = arrayPositions(data)
    newlinesToRemove = []
    for start, end in zip(openBracketPositions, closeBracketPositions):
        # find the commas followed by newlines
        
        arrayNewlines = list(re.finditer(',\\n +', data[start: end]))
#         print(len(arrayNewlines))
        del arrayNewlines[everyN-1::everyN] # keep these ones!
#         print(len(arrayNewlines))
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