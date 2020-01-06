# PrettifyJSON
 Truncates the number of decimal places and sets the number of array entries per line.

Usage: PrettifyJSON.py filename numberOfDecimalPlacesToTruncateFloatsTo numberOfColumnsPerLineOfArray
* numberOfDecimalPlacesToTruncateFloatsTo: decides how many decimal places to truncate to. JKI JSON library for LabVIEW defaults to far too many.
* numberOfColumnsPerLineOfArray: decides where the linebreak occurs in an array section. Each line will have N comma separated entries.

A LabVIEW vi for calling this script is included.

Also, a set of example raw and reformated/prettified JSONs is included.
