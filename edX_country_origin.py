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
  country_count['united states'] = 0
  count = 0
  
  for pair in email_addr:
    try:
      response = {}
      if pair[1] != '':
        response = calais.analyze(pair[1])
      # if the addr contains country information
      name = ''
      if hasattr(response, 'entities'):
        print response.entities
        name = response.entities[0]['containedbycountry'].lower()
        if '@' in name: #where email addresses are wrongly entered as addr
          last_str = pair[0].split('.')[-1].lower()
          if last_str in country_code:
            name = country_code[last_str]
          else:
            name = 'united states'
          if name not in country_count:
            country_count[name] = 1
          else:
            country_count[name] = country_count[name]+1
        else:
          if name not in country_count:
            country_count[name] = 1
          else:
            country_count[name] = country_count[name]+1
      # otherwise, check the email addr    
      else:
        last_str = pair[0].split('.')[-1].lower()
        if last_str in country_code:
          name = country_code[last_str]
        else:
          name = 'united states'
        if name not in country_count:
          country_count[name] = 1
        else:
          country_count[name] = country_count[name]+1
    except ValueError:
      print 'Calais could not handle the language'
    count = count +1
    print 'Number of entries queried: ' + str(count)
  
  print country_count

  with open('countrybreakdown.csv', 'w') as fp:
    a = csv.writer(fp, delimiter=',')
    for key in country_count:
      a.writerow([key, country_count[key]])
      
if __name__ == "__main__":
  main()


