#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import datetime
import requests
import csv

baseUrl = 'https://www.commonfloor.com'
searchUrl = 'https://www.commonfloor.com/listing-search?city=Bangalore&prop_name%5B%5D={0}&property_location_filter%5B%5D=area_142&use_pp=0&set_pp=1&polygon=1&page=1&page_size=30&search_intent=rent&min_inr=10000&max_inr=25000&bed_rooms%5B%5D=2'

areas = ["Cambridge+Layout", "Indira+Nagar","Indira+Nagar", "New+Thippasandra", "Domlur", "Sampangi+Rama+Nagar", "Shanthi+Nagar", "Wilson+Garden", "Richmond+Town", "Richmond+Road"]

#areas = ['Cambridge+Layout']
requiredFields = ['Area', 'Rent', 'Furnishing State', 'Property on', 'Builtup Area',
                  'Security Deposit', 'Year of Construction']

filteredHouseDetails = {}

maxRecords = 1000

def retrievePage(url):
    s = requests.Session()
    r = s.get(url)
    data = r.text
    soup = BeautifulSoup(data)

    # print soup.encode("utf-8")

    return soup


def getRequiredDetails(props):
    reqDetails = {}

    # print "RAW PROPS"
    # print props
    # print "---------"

    for field in requiredFields:
        value = ''
        if field in props:
            value = props[field]
        reqDetails[field] = value
    return reqDetails


def isPostedByOwner(property):
    return 'Brokerage terms' not in property

def getHouseRent(soup):
    rentDiv = soup.find('p', {'class': 'proj-value'})
    #print rentDiv
    return rentDiv.find('span').text

def crawl(area, url):
    soup = retrievePage(url)
    recordCount = 1
    for link in soup.find_all('a'):
        if recordCount > maxRecords:
            break
        href = str(link.get('href'))
        if href.find('/listing') != -1:
            print 'Crawling ' + href + '....'
            detailsPage = retrievePage(baseUrl + href)
            detailsDiv = detailsPage.find('div',
                    {'class': 'otherDetails'})
            houseDetails = {}
            houseDetails['Area'] = area

            houseRent = getHouseRent(detailsPage)
            houseDetails['Rent'] = houseRent

            print 'Rent:' + houseRent
            
            for field in detailsDiv.find_all('div'):
                title = field.find('p', {'class': 'title'}).text
                value = field.find('p', {'class': 'propStatus'}).text

                print title + ':' + value
                houseDetails[title] = value

            if isPostedByOwner(houseDetails):
				print 'Added!!! ' + baseUrl + href
				print getRequiredDetails(houseDetails)
				recordCount += 1
				filteredHouseDetails[baseUrl + href] = \
	                getRequiredDetails(houseDetails)
            else:
	            print 'Rejected!!!'


def getAreaUrl(area):
    url = searchUrl
    return url.format(area)


def searchHouses(areas):
    for area in areas:
        print area
        crawl(area, getAreaUrl(area))

def getColumnHeadings():
    headings = ['URL']
    headings.append(requiredFields)
    return ['URL'] + requiredFields

def getCSVFileName():
    return 'houseDetails_{:%Y_%m_%d_%H_%M_%S}.csv'.format(datetime.datetime.now())

def exportDataToCSV(data):
    print 'Exporting the data to CSV file.......'
    csvData = []
    csvData.append(getColumnHeadings());

    fileName = getCSVFileName()

    with open(fileName, 'w') as fp:
        a = csv.writer(fp, delimiter=',')
        for row in data:
            curCSVRow = [row]
            for field in requiredFields:
                curCSVRow.append(data[row][field])
            csvData.append(curCSVRow)
        a.writerows(csvData)

    print 'Data export completed. File: ' + fileName

#Main Code - Start
searchHouses(areas)

print 'Filtered House details'
print filteredHouseDetails

exportDataToCSV(filteredHouseDetails)
#Main Code - End