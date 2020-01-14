# Used to call scripts while inside Sublime editor without resorting to commandline.
from PrettifyJSON import *

fName = 'He_SAS_191213_0935.json'

maxDP = 3
everyN = 20
    

print(f"FileName: {fName}")
print(f"Max Number of Decimals Places: {maxDP}")
print(f"Max Array Entries Per Line: {everyN}")

with open(fName, 'r', encoding="utf-8") as JSONfile:
    data = JSONfile.read()

excessFloatZeroesRemovedData = roundDecimalPlaces(data, maxDP)
result = reformatArrays(excessFloatZeroesRemovedData, everyN)

newFName = fName[:-5] +'_formatted.json'
with open(newFName, 'w', encoding="utf-8") as JSONfile:
    JSONfile.write(result)