# -*- coding: utf-8 -*-
"""Find sales prices of various types of properties sold in a given
period of time and prepare for plotting on a map with R.
"""

""" Example URL
http://services.kortforsyningen.dk/?servicename=RestGeokeys_v2&method=adresse&vejnavn=Grundtvigs+Alle&husnr=7&postnr=6700&hits=50&geometry=true&login=timroerstroem&password=
"""

# Plotting should be done with Vega-Lite and Altail.

import requests
import bs4
import datetime
import math

currentYear = datetime.datetime.now().year
propertyTypes = ['villa', 'ejerlejlighed']


def numPages(firstYear, lastYear, propType):
    """ Find the number of pages we have to iterate through to get all the
    results we want. Each page contains 40 results; this should probably be
    verified by looking at the text.
    """
    # Get the page and check the result is good
    propURL = str('http://www.boliga.dk/salg/resultater?so=1&type=' +
                  propType + '&fraPostnr=1000&tilPostnr=9990&minsaledate=' +
                  firstYear + '&maxsaledate=' + lastYear)
    resPropNo = requests.get(propURL)
    resPropNo.raise_for_status()

    # Parse the result
    propNoSoup = bs4.BeautifulSoup(resPropNo.text, 'html.parser')

    # Extract the total number of results from the text above the results table
    propNoArr = propNoSoup.select('td[class="text-center"] > label'
                                  )[0].getText().split()

    for i in range(len(propNoArr)):
        try:
            # Is the element a number?
            int(propNoArr[i])
        except ValueError:
            # Not a number, next element
            continue
        # The only element that is a number is the total number of results
        propNo = propNoArr[i]

    # Return value is the number of pages with 40 results per page
    pageNo = math.ceil(propNo, 40)

    return pageNo


def getPrices(firstYear, lastYear, propType):
    """ Get the prices of the given property type for the given years. Also
    extract the addresses, we will use these to find the geographic
    coordinates of the properties later.
    """
    pages = numPages(firstYear, lastYear, propType)
    props = {'address': [], 'price': [], 'coords': []}

    # The generic URL without page number
    genURL = str('http://www.boliga.dk/salg/resultater?so=1&type=' + propType +
                 '&kom=&fraPostnr=1000&tilPostnr=9990&minsaledate=' +
                 firstYear + '&maxsaledate=' + lastYear + '&p=')

    # The stop-value for range() is one higher than the last returned value
    for i in range(1, pages + 1):
        # Get each page and check for errors
        resProp = requests.get(genURL + i)
        resProp.raise_for_status()

        # Make soup
        propSoup = bs4.BeautifulSoup(resProp.text, 'html.parser')

        # The site doesn't use <tbody>, <tr> is directly inside <table>
        rows = propSoup.select('#searchresult > tr')

        # Find address and price per m^2 for each row
        for j in range(40):
            address = str(rows[j].a.contents[0] + ' ' + rows[j].a.contents[2])
            price = float(rows[j].select('td')[3].getText().replace('.', ''))

            # Assign the values to a dictionary
            props['address'].append(address)
            props['price'].append(price)

while True:
    try:
        # We should probably default to the current year
        startYear = int(input("Starting year: "))
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
            print("Please enter a year between " + str(startYear+1) + " and " +
                  currentYear + ".")
            continue
        if int(endYear) <= startYear:
            print("End year must be greater than starting year (" +
                  str(startYear) + ").")
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
print("This program should fetch prices from " + str(startYear) + " until " +
      str(endYear) + ".")
