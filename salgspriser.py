# Find sales prices of various (or all?) types of properties sold in a given
# period of time and prepare for plotting on a map with R

import requests, bs4, datetime

currentYear = datetime.datetime.now().year

while True:
    try:
        startYear = int(input("Starting year: "))
    except ValueError:
        # User did not enter a valid year
        print("Please enter a year between 1992 and " + str(currentYear))
        # Back to start
        continue
    if startYear < 1992 or startYear > currentYear:
        # There are no data before 1992 or for the future
        print("Please enter a year between 1992 and " + str(currentYear))
        # Back to start
        continue
    else:
        # Success
        break
