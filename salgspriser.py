# -*- coding: utf-8 -*-
"""Find sales prices of various types of properties sold in a given
period of time and prepare for plotting on a map with R.
"""

import requests
import bs4
import datetime
import math
import json
import pygeoj

CURRENT_YEAR = datetime.datetime.now().year
PROPERTY_TYPES = ['villa', 'ejerlejlighed']
EXTREMES = [57.8, 8, 54.5, 15.2]  # N,W,S,E in degrees


def num_pages(first_year, last_year, property_type):
    """Find the number of pages we have to iterate through to get all the
    results we want. Each page contains 40 results; this should probably be
    verified by looking at the text.
    """
    # Get the page and check the result is good
    property_URL = str('http://www.boliga.dk/salg/resultater?so=1&type='
                       + property_type + '&fraPostnr=1000&tilPostnr=9990'
                       + '&minsaledate=' + first_year + '&maxsaledate='
                       + last_year)
    res_prop_num = requests.get(property_URL)
    res_prop_num.raise_for_status()

    # Parse the result
    prop_num_soup = bs4.BeautifulSoup(res_prop_num.text, 'html.parser')

    # Extract the total number of results from the text above the results table
    prop_num_array = prop_num_soup.select(
        'td[class="text-center"] > label'
        )[0].getText().split()

    for i in range(len(prop_num_array)):
        try:
            # Is the element a number?
            int(prop_num_array[i])
        except ValueError:
            # Not a number, next element
            continue
        # The only element that is a number is the total number of results
        prop_num = prop_num_array[i]

    # Return value is the number of pages with 40 results per page
    page_num = math.ceil(prop_num, 40)

    return page_num


def address_coords(street, houseno, postcode):
    """Convert an address into a set of coordinates.
    """

    with open('passwd.cfg') as f:
        credentials = [x.strip().split(':') for x in f.readlines()]

    url = str('http://services.kortforsyningen.dk/?servicename='
              + 'RestGeokeys_v2&method=adresse&vejnavn=' + street + '&husnr='
              + houseno + '&postnr=' + postcode + '&hits=1&geometry=true'
              + '&outgeoref=EPSG:4326&login=' + credentials[0] + '&password='
              + credentials[1])
    res = requests.get(url)
    res.raise_for_status()

    # There is a syntax error in the input geojson data
    data = pygeoj.load(data=json.loads(res.text.replace('POINT', 'Point')))

    coords = data[0].geometry.coordinates

    return coords


def get_prices(first_year, last_year, property_type):
    """Get the prices of the given property type for the given years. Also
    extract the addresses, we will use these to find the geographic
    coordinates of the properties later.
    """

    # Placeholder
    props = {'address': [], 'price': [], 'lat': [], 'lon': []}

    # Get the number of pages
    pages = num_pages(first_year, last_year, property_type)

    # The generic URL without page number
    generic_URL = str('http://www.boliga.dk/salg/resultater?so=1&type='
                      + property_type + '&fraPostnr=1000&tilPostnr=9990'
                      + '&minsaledate=' + first_year + '&maxsaledate='
                      + last_year + '&p=')

    # The stop-value for range() is one higher than the last returned value
    for i in range(1, pages + 1):
        # Get each page and check for errors
        res_prop = requests.get(generic_URL + i)
        res_prop.raise_for_status()

        # Make soup
        prop_soup = bs4.BeautifulSoup(res_prop.text, 'html.parser')

        # The site doesn't use <tbody>, <tr> is directly inside <table>
        rows = prop_soup.select('#searchresult > tr')

        # Find address and price per m^2 for each row
        for j in range(40):
            price = float(rows[j].select('td')[3].getText().replace('.', ''))

            # Split the address
            street = str(rows[j].a.contents[0]).rsplit(' ', 1)[0]
            houseno = str(rows[j].a.contents[0]).rsplit(' ', 1)[1]
            postcode = str(rows[j].a.contents[2]).split()[0]

            coordinates = address_coords(street, houseno, postcode)

            # Assign the values to a dictionary
            props['address'].append(str(street + ' ' + houseno + ' '
                                    + postcode))
            props['price'].append(price)
            props['lat'].append(coordinates[1])
            props['lon'].append(coordinates[0])

    return props


def avg_prices(prices):
    """Find the average price per square metre for properties inside areas of
    a pre-defined size (1 km^2).
    """


while True:
    try:
        # We should probably default to the current year
        start_year = int(input("Starting year: "))
    except ValueError:
        # User did not enter a valid year
        print("Please enter a year between 1992 and " + str(CURRENT_YEAR)
              + ".")
        # Back to start
        continue
    if start_year < 1992 or start_year > CURRENT_YEAR:
        # There are no data before 1992 or for the future
        print("Please enter a year between 1992 and " + str(CURRENT_YEAR)
              + ".")
        # Back to start
        continue
    else:
        # Success
        break

if start_year == CURRENT_YEAR:
    end_year = 'today'
else:
    while True:
        end_year = input("End year (or leave blank for today): ")
        if end_year == '' or end_year == 'today':
            # No input, end date is today, also silently accept 'today'
            end_year = 'today'
            break
        try:
            # Check if user input is an integer
            int(end_year)
        except ValueError:
            # Not an integer, back to start
            print("Please enter a year between " + str(start_year+1) + " and "
                  + CURRENT_YEAR + ".")
            continue
        if int(end_year) <= start_year:
            print("End year must be greater than starting year ("
                  + str(start_year) + ").")
            continue
        elif int(end_year) > CURRENT_YEAR:
            # Assume user wants all data until today
            print("Future date given, assuming today.")
            endYear = 'today'
            break
        else:
            # All is good
            break

# Preliminary output to validate the above
print("This program should fetch prices from " + str(start_year) + " until "
      + str(endYear) + ".")
