'''
python2 create_dataset.py  <original csv file>
'''

import csv
import sys
import math

# translate currency to numbers
#http://stackoverflow.com/questions/8421922/how-do-i-convert-a-currency-string-to-a-floating-point-number-in-python
from re import sub
from decimal import Decimal

def main():

    filename = sys.argv[1]
    counter = 0
    data = []
    with open(filename, 'rb') as csvfile:
        csvreader = csv.reader(csvfile, delimiter = ',', quotechar = '"')
        for row in csvreader:
            if counter > 0: # we want to not append the first line
                row = [w.replace(',', ' ') for w in row]
                row = [w.replace('"', '') for w in row]
                data.append(row)
            else:
                print row # just to see what we have in total
            counter += 1
            if counter > 50000:
                break

    # ['Year', 'Ethnicity', 'Sex', 'Cause of Death', 'Count', 'Percent']
    #   0           1           2           3           4           5

    csvfile.close()

    print 'Testing Data Trimming'
    print data[4]
    #new_data = remove_column(data, 5)

    if filename == 'Civil_List_2014.csv':
        for item in data:
            value = Decimal(sub(r'[^\d.]', '', item[5]))
            value = int(value / 10000)
            #value = math.floor(value)
            item[5] = '$' + str(value) + '0K'
            if value > 5:
                item.append('Above 50K')
            else:
                item.append('Below 50K')

        new_data = remove_column(data, 4) # Eliminate columns to see interesting results
        new_data = remove_column(data, 1)
        new_Data = remove_column(data, 0)

    print new_data[4]

    datafile  = open('INTEGRATED-DATASET.csv', "wb")
    csvwriter = csv.writer(datafile)

    for row in new_data:
        csvwriter.writerow(row)
    datafile.close()

def remove_column(data, index):
    for row in data:
        row.pop(index)
    return data

if __name__=="__main__":
    main()
