#!/usr/bin/python

from __future__ import division
import base64
import collections
import string
import sys
import unicodedata
import urllib
import urllib2
import os
import re
import xml.etree.ElementTree as ET
from collections import Counter


# Account key to query Bing
ACCOUNT_KEY = 'XuOLiXL26shewnIRN64uXZ339idWvzPDLOK6u022udM'

# Query sent to Bing, to be formatted with the actual query
BING_URL = ('https://api.datamarket.azure.com/Data.ashx/Bing/SearchWeb/v1/'
            'Composite?Query=%27site%3a{}%20{}%27&$top=10&$format=Atom')

# Data services prefix, used in retrieving Bing's results, to be formatted with
# the desired field
DATA_SERVICES_PREFIX = ('{{http://schemas.microsoft.com/ado/2007/08/'
                        'dataservices}}{}')

# W3 prefix, used in retrieving Bing's results, to be formatted with the desired
# field
W3_PREFIX = '{{http://www.w3.org/2005/Atom}}{}'

# Basic stop words which we do not use to augment queries.
STOP_WORDS = ['the', 'to', 'of', 'and', 'is', 'in', 'it', 'from', 'an', 'a',
              'on', 'with']

# Max number of documents to retrieve for each query
NUM_DOCS_TO_RETRIEVE = 4


# Parse a raw XML string from a Bing query response into a dictionary.
def parse_xml(raw_response):
    tree = ET.parse(raw_response)
    # Get the root of the DOM so we can iterate through the elements.
    root = tree.getroot()

    retrieved_urls = []
    num_docs_retrieved = 0

    for entry in root.iter():
        if (entry.tag == W3_PREFIX.format('content') and
            num_docs_retrieved < NUM_DOCS_TO_RETRIEVE):
            for sub_entry in entry.iter():
                if sub_entry.tag == DATA_SERVICES_PREFIX.format('Url'):
                    retrieved_urls.append(sub_entry.text)
                    num_docs_retrieved += 1
        if entry.tag == DATA_SERVICES_PREFIX.format('WebTotal'):
            num_results = int(entry.text)

    return num_results, retrieved_urls


# Sets up query matrix for our tree of categories
def setup_query_list(FILENAME):
    if FILENAME == 'root':
        category_list = ['Computers', 'Health', 'Sports']
        query_list = [[], [], []]
    elif FILENAME == 'computers':
        category_list = ['Hardware', 'Programming']
        query_list = [[], []]
    elif FILENAME == 'health':
        category_list = ['Fitness', 'Diseases']
        query_list = [[], []]
    elif FILENAME == 'sports':
        category_list = ['Basketball', 'Soccer']
        query_list = [[], []]

    # Parse the queries, removing the category name first
    with open(FILENAME + '.txt', 'r') as f:
        for line in f:
            sp = line.strip().split(' ')
            category = sp.pop(0)
            list_index = category_list.index(category)
            query_list[list_index].append(' '.join(sp))

    return query_list


# Get all queries for the categories
def get_query_list():
    files = ['root', 'computers', 'health', 'sports']
    all_query_lists = []

    for f in files:
        all_query_lists.append(setup_query_list(f))

    return all_query_lists


# Remove whitespace, punctuation, etc. from a word; turn it into a lower case
# string with only alphanumeric characters.
def clean_word(word):
    if type(word) is str:
        return filter(str.isalpha, word).lower()
    elif type(word) is unicode:
        # Normalize unicode and turn it into ASCII
        non_unicode_word = (unicodedata.normalize('NFKD', word).
            encode('ascii', 'ignore'))
        return filter(str.isalpha, non_unicode_word).lower()


# Given coverage and specificity vectors and their thresholds, create a vector
# which has:
# 0 in a position if the thresholds are not satisfied
# 1 in a position if the thresholds are satisfied
def classify_vector(cov_vector, spec_vector, t_ec, t_es):
    c_vector = []
    # Iterate through the vectors and see if the thresholds are satisfied
    for i in range(len(spec_vector)):
        if (cov_vector[i] > t_ec and spec_vector[i] > t_es):
            c_vector.append(1)
        else:
            c_vector.append(0)
    return c_vector


# This function takes the query list, and other parameters, and returns the
# score vector for the query list
def query_bing(query_list, host, headers):
    score_vector = []
    all_retrieved_urls = []
    for category_list in query_list:
        current_sum = 0
        for query_term in category_list:
            query_term_encoded = urllib.quote(query_term, safe='')

            req = urllib2.Request(BING_URL.format(host, query_term_encoded),
                                headers=headers)
            raw_response = urllib2.urlopen(req)

            num_results, retrieved_urls = parse_xml(raw_response)
            current_sum += num_results
            all_retrieved_urls += retrieved_urls
        score_vector.append(current_sum)

    return score_vector, all_retrieved_urls


# This function takes the depth vector as input, and returns a string of how
# the query is categorized. The output string puts each category on a new line,
# indenting if the category is a subcategory of the previous level. This allows
# us to easily represent a database that falls under multiple categories.
def get_result(depth_vector):
    cat = 'Root\n'
    row_count = -1
    for row in depth_vector:
        row_count = row_count + 1
        col_count = -1
        if (-1 not in row):
            cat += '  ' + get_category(row_count) + '\n'
            for col in row:
                col_count = col_count + 1
                if col == 1:
                    cat += '    ' + get_subcategory(row_count, col_count) + '\n'

    return cat


def get_subcategory(row, col):
    subcategories = [['Hardware', 'Programming'],
                     ['Fitness', 'Diseases'],
                     ['Basketball', 'Soccer']]
    return subcategories[row][col]


def get_category(row):
    categories = ['Computers', 'Health', 'Sports']
    return categories[row]


# Performs the lynx -dump command through the terminal.
# Must have lynx installed if using from a local machine:
# http://lynx.invisible-island.net/current/
def lynx_dump(html_link):
    cmd = os.popen("lynx --dump '%s'" % html_link)
    output = cmd.read()
    cmd.close()
    return output


# Turn raw output from 'lynx --dump' into a list of usable words
def process_lynx(data):
    # First, remove everything in the references section
    ref_index = data.rfind('\nReferences\n')
    if ref_index == -1:
        ref_index = len(data)
    data_no_ref = data[:ref_index]

    # Remove everything within brackets using a regex
    regex = re.compile('\[.+?\]')
    output = regex.sub('', data_no_ref)
    # Split the output by whitespace
    output = output.split()

    # Using clean_word function to clean each word in the list
    for w in range(len(output)):
        output[w] = clean_word(output[w])
    # Removing all empty strings from list
    while '' in output:
        output.remove('')

    return output

# This function takes a list of urls, takes the contents, and constructs a
# content summary.
def lynx_dict(url_list):
    my_dict = collections.defaultdict(int)
    for my_url in url_list:
        # Skip PDFs; they generate a bunch of gibberish words if used raw
        if my_url.find('.pdf') != -1:
            continue
        # To keep track of words we have seen
        word_dict = collections.defaultdict(int)
        lynx_raw_data = lynx_dump(my_url)
        lynx_wordlist = process_lynx(lynx_raw_data)

        for word in lynx_wordlist:
            if word not in word_dict:
                word_dict[word] += 1
                my_dict[word] += 1
    return my_dict

# Takes in classification string (ie. Root, Health, Sports, or Computers), host,
# and content summary, and prints values to a .txt file
def write_to_file(classification, host, my_dict):
    my_file = open(classification + '-' + host + '.txt', 'w')
    for key, value in sorted(my_dict.items()):
        my_file.write(key + '#' + str(value) + '\n')
    my_file.close()

def main():
    # The first argument passed after the desired query string will be the
    # specificity threshold.
    t_es = float(sys.argv[1])
    # The second argument passed after the python script name will be the
    # coverage threshold.
    t_ec = float(sys.argv[2])
    #The third argument passed after the python script name will be the host.
    host = sys.argv[3]

    # This function processes the files and returns a query matrix for all files
    query_list = get_query_list()

    # Constants
    account_key_enc = base64.b64encode('{}:{}'.format(ACCOUNT_KEY, ACCOUNT_KEY))
    headers = {'Authorization': 'Basic {}'.format(account_key_enc)}

    # Converts the host and query term to HTML5 URL ready code.
    host_encoded = urllib.quote(host, safe='')

    # gets the query list for the root file
    root_query_list = query_list[0]

    print("\nSending queries. This whole process may take a few minutes.\n")

    root_coverage, root_urls = query_bing(root_query_list, host, headers)
    root_urls = list(set(root_urls))

    root_dict = lynx_dict(root_urls) 

    root_coverage_sum = sum(root_coverage)
    root_specificity = [x / float(root_coverage_sum) for x in root_coverage]
    root_thresholds_hit = classify_vector(
        root_coverage, root_specificity, t_ec, t_es)

    print("Coverage and specificity vectors for Root:")
    print(root_coverage)
    print(root_specificity)
    print

    categories_thresholds_hit = []
    sub_dict_list = []
    for i in range(len(root_thresholds_hit)):
        if root_thresholds_hit[i]:
            current_query_list = query_list[i+1]
            coverage, urls = query_bing(current_query_list, host, headers)
            urls = list(set(urls))

            # Content summary of the subcategory
            sub_dict = lynx_dict(urls)
            sub_dict_list.append(sub_dict)

            coverage_sum = sum(coverage)
            specificity = [x / float(coverage_sum) for x in coverage]
            category_threshold_hit = classify_vector(
                coverage, specificity, t_ec, t_es)

            print("Coverage and specificity vectors for {}:".format(
                get_category(i)))
            print(coverage)
            print(specificity)
            print
            categories_thresholds_hit.append(category_threshold_hit)
        else:
            categories_thresholds_hit.append([-1, -1])

    # The depth vector winds up being a 3x2 matrix.
    # The rows represent the greater topics, the columns represent specific
    # subcategories.
    #
    # - If there is a -1 in a row (either col), that means that the broader
    #   category doesn't qualify; -1 is just a placeholder for this case.
    # - If there is a 0, that means the subcategory doesn't qualify
    # - If there is a 1, that means the subcategory qualifies
    result = get_result(categories_thresholds_hit)
    print 'Classification of ' + host + ': \n' + result

    classes = [c.strip() for c in result.split('\n')]

    # If we have at least one subclass beyond 'Root', make content summaries.
    # This code accounts for the possibility that a database will fall under
    # multiple subcategories.
    if len(classes) > 1: 
        class_counter = 0
        for current_sub in sub_dict_list:
            if len(sub_dict_list) > 1:
                while not root_thresholds_hit[class_counter]:
                    class_counter += 1
                classification = get_category(class_counter)
                # Keep track of the class counter for the next loop
                class_counter += 1
            else:
                # Simply get the subcategory
                classification = classes[1]

            # Write the subcategory content summary to its own file
            write_to_file(classification, host, current_sub)

            for item in current_sub:
                if item in root_dict:
                    root_dict[item] += current_sub[item]
                else:
                    root_dict[item] = current_sub[item]

    # Now we can output all of our root stuff to text files.
    write_to_file('Root', host, root_dict)


if __name__=="__main__":
    main()
