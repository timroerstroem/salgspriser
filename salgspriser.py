""" Find sales prices of various (or all?) types of properties sold in a given
period of time and prepare for plotting on a map with R
"""

# It is possible that the module 'vincent' could do the plotting

import requests, bs4, datetime

currentYear = datetime.datetime.now().year

while True:
    try:
        startYear = int(input("Starting year: ")) # Should probably default to the current year
    except ValueError:
        # User did not enter a valid year
        print("Please enter a year between 1992 and " + str(currentYear) + ".")
        # Back to start
        continue
    if startYear < 1992 or startYear > currentYear:
        # There are no data before 1992 or for the future
        print("Please enter a year between 1992 and " + str(currentYear) + ".")
        # Back to start
        continue
    else:
        # Success
        break

if startYear == currentYear:
    endYear = 'today'
else:
    while True:
        endYear = input("End year (or leave blank for today): ")
        if endYear == '' or endYear == 'today':
            # No input, end date is today, also silently accept 'today'
            endYear = 'today'
            break
        try:
            # Check if user input is an integer
            int(endYear)
        except ValueError:
            # Not an integer, back to start
            print("Please enter a year between " + str(startYear+1) + " and " + currentYear + ".")
            continue
        if int(endYear) <= startYear:
            print("End year must be greater than starting year (" + str(startYear) + ").")
            continue
        elif int(endYear) > currentYear:
            # Assume user wants all data until today
            print("Future date given, assuming today.")
            endYear = 'today'
            break
        else:
            # All is good
            break

# Preliminary output to validate the above
print("This program should fetch prices from " + str(startYear) + " until " + str(endYear) + ".")
