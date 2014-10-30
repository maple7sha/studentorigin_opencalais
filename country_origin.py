#!/usr/bin/python
# coding: utf8

import sys
import hashlib
import urllib
import hmac
import base64
import urlparse
import csv
import json
from calais import Calais

def main():
  # read in csv file to extract the email and addresses field
  # put email and addr into a list of tuples 
  email_addr = []
  with open('OECx_PH241x_3T2014_student_profile_info_2014-10-20-1645.csv', 'rU') as f:
      reader = csv.reader(f)
      for row in reader:
          pair = [row[3], row[9]]
          email_addr.append(pair)

  # create dictionary to find the country code | to iterate over the dictionary=> for key in d:
  country_code = {}
  with open('Country_code.csv', 'rU') as f:
      reader = csv.reader(f)
      for row in reader:
          key = row[0].split(' ', 1)[0].lower()
          value = row[0].split(' ', 1)[1].lower()
          country_code[key] = value

  # make Calais calls to extract country name
  api_key = 'wukyjrm778py5wry9qdtgk9u'
  calais = Calais(api_key)

  # dictionary to store all the results
  country_count = {}
  country_count['(TOTAL)'] = 0
  country_count['united states'] = 0
  country_count['~origin unknown'] = 0
  count = 0
  

  for pair in email_addr:
    check = 0
    try:
      response = {}
      if pair[1] != '':
        response = calais.analyze(pair[1])
        # if the addr contains country information
        if hasattr(response, 'entities'):
          # entry is a list of 3 elements: priority (3 for ProvinceOrState, 2 for Country, 1 for EmailAddress ), Country, Province 
          entry = [-1, '', '']
          for each in response.entities:
            if each['_type'] == 'ProvinceOrState':
              
              try: 
                entry[1] = each['resolutions'][0]['containedbycountry'].lower()
                entry[0] = 3
                entry[2] = each['name'].lower()
              except KeyError:
                print 'Country name cannot be retrieved'

            elif each['_type'] == 'Country':
              if entry[0] < 2:
                entry[0] = 2
                entry[1] = each['name'].lower()
            elif each['_type'] == 'EmailAddress':
              if entry[0] < 1:
                entry[0] = 1

          if entry[0] == 3:
            name = '(US) - ' + entry[2]
            if entry[1] not in country_count:
              country_count[entry[1]] = 1
            else:
              country_count[entry[1]] = 1 + country_count[entry[1]]
              if entry[1] == 'united states':
                if name not in country_count:
                  country_count[name] = 1 
                else:
                  country_count[name] = 1 + country_count[name] 

          elif entry[0] == 2:
            if entry[1] not in country_count:
              country_count[entry[1]] = 1   
            else:
              country_count[entry[1]] = 1 + country_count[entry[1]]

          elif entry[0] == 1:
            check = 1 # go through email check

          else:
            country_count['~origin unknown'] = country_count['~origin unknown'] + 1

      else: 
        check = 1

      # if addr is empty, query email address mapping table; if no entry, Unknown add 1
      # here we assume that all entries without addr and without strong indication of country origins in their emails will be categorized under the USA entry
      if check == 1: 
        # determine entry name
        email_endstr = pair[0].split('.')[-1].lower()
        if email_endstr in country_code:
          name = country_code[email_endstr]
        else:
          name = '~origin unknown'  
        # add entry 
        if name not in country_count:
          country_count[name] = 1
        else:
          country_count[name] = country_count[name]+1

    except ValueError:
      print 'Calais could not handle the language'
      country_count['~origin unknown'] = country_count['~origin unknown'] + 1
    count = count +1
    print 'Number of entries queried: ' + str(count)
  
  country_count['(TOTAL)'] = count
  country = sorted(country_count)

  print country
  us = 0
  with open('origin.csv', 'w') as fp:
    a = csv.writer(fp, delimiter=',')
    for key in country:
      if key != 'united states':
        a.writerow([key, country_count[key]])
      if us == 0:
        a.writerow(['united states', country_count['united states']])
        us = 1
      



if __name__ == "__main__":
  main()


