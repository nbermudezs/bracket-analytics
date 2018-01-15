# bracket-analytics
Analysis of 1985-Present NCAA Men's Basketball Tournament Brackets as 63-bit vectors. 

Source: http://fs.ncaa.org/Docs/stats/m_final4/2018/MFFBook.pdf

The brackets were manually entered (see "ManuallyCreatedTextFiles" folder),
then converted into JSON files ("AutoCreatedJsonFiles" folder) that were
merged and converted to generate the different representations and groupings
in the "Brackets" folder.

The "Python" folder contains Python scripts and class definitions that help
format, convert, and analyze the brackets. 

For example, executing "./Python/countWinsPerSeed.py Brackets/TTT/allBracketsTTT.json" generates tables that match those at
http://bracketodds.cs.illinois.edu/seedadv.html. 

Some Python scripts use relative paths to access the brackets, so execute
them from the parent directory (e.g. "./Python/countWinsPerSeed.py"). 

Source for chi-square critical values: http://www.itl.nist.gov/div898/handbook/eda/section3/eda3674.htm.