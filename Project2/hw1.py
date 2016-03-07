#!/usr/bin/python

from __future__ import division
import base64
import collections
import string
import sys
import unicodedata
import urllib
import urllib2
import xml.etree.ElementTree as ET


# Account key to query Bing
ACCOUNT_KEY = 'Tbd+aKdy89bDQLqp6Hwby15SssvSLCUVPnAQaVXRIPg'

# Query sent to Bing, to be formatted with the actual query
BING_URL = ('https://api.datamarket.azure.com/Bing/Search/Web?Query=%27{}'
            '%27&$top=10&$format=Atom')

# Data services prefix, used in retrieving Bing's results, to be formatted with
# the desired field
DATA_SERVICES_PREFIX = ('{{http://schemas.microsoft.com/ado/2007/08/'
                        'dataservices}}{}')

# Basic stop words which we do not use to augment queries.
STOP_WORDS = ['the', 'to', 'of', 'and', 'is', 'in', 'it', 'from', 'an', 'a',
              'on', 'with']


# Parse a raw XML string from a Bing query response into a dictionary where
# the keys are the number of the response and the values are themselves
# dictionaries with key/value pairs as component type and component value.
def parse_xml(raw_response):
    tree = ET.parse(raw_response)
    # Get the root of the DOM so we can iterate through the elements.
    root = tree.getroot()
    main_list = dict()
    index = 0

    for entry in root.iter(tag='{http://www.w3.org/2005/Atom}entry'):
        index += 1
        main_list[index] = {'Title': '', 'Description': '', 'URL':'' }
        for entry2 in entry.iter():
            if entry2.tag == DATA_SERVICES_PREFIX.format('Title'):
                main_list[index]['Title'] = entry2.text
            if entry2.tag == DATA_SERVICES_PREFIX.format('Description'):
                main_list[index]['Description'] = entry2.text
            if entry2.tag == DATA_SERVICES_PREFIX.format('Url'):
                main_list[index]['URL'] = entry2.text

    print '\nTotal number of results: {}'.format(index)
    return main_list


# Given all responses for a Bing query, get the relevant responses by getting
# input from the user.
def classify_responses(all_responses):
    relevant_responses = {}
    irrelevant_responses = {}

    for key in all_responses:
        print (u'\n=========================\n\n'
                'RESULT {}\n'
                'Title: {}\n'
                'URL: {}\n'
                'Description: {}\n').format(
               key, all_responses[key]['Title'], all_responses[key]['URL'],
               all_responses[key]['Description'])

        valid_user_response_received = False
        while not valid_user_response_received:
            user_judgment = raw_input('Relevant? Y/N: ')

            if user_judgment.lower() == 'y':
                relevant_responses[key] = all_responses[key]
                valid_user_response_received = True
            elif user_judgment.lower() == 'n':
                irrelevant_responses[key] = all_responses[key]
                valid_user_response_received = True
            else:
                print 'Invalid response.'

    return relevant_responses, irrelevant_responses


# Given all the relevant responses, we construct a table of word frequencies,
# where a word count is incremented if it appears in a relevant response and
# decremented if it appears in an irrelevant response.
def build_frequency_table(relevant_responses, irrelevant_responses):
    frequency_table = collections.defaultdict(int)

    for key in relevant_responses:
        for word in relevant_responses[key]['Title'].split(' '):
            cleaned_word = clean_word(word)
            if len(cleaned_word) > 0:
                frequency_table[cleaned_word] += 1
        for word in relevant_responses[key]['Description'].split(' '):
            cleaned_word = clean_word(word)
            if len(cleaned_word) > 0:
                frequency_table[cleaned_word] += 1

    for key in irrelevant_responses:
        for word in irrelevant_responses[key]['Title'].split(' '):
            cleaned_word = clean_word(word)
            if len(cleaned_word) > 0:
                frequency_table[cleaned_word] -= 1
        for word in irrelevant_responses[key]['Description'].split(' '):
            cleaned_word = clean_word(word)
            if len(cleaned_word) > 0:
                frequency_table[cleaned_word] -= 1

    return frequency_table


# Remove whitespace, punctuation, etc. from a word; turn it into a lower case
# string with only alphanumeric characters.
def clean_word(word):
    if type(word) is str:
        return filter(str.isalnum, word).lower()
    elif type(word) is unicode:
        # Normalize unicode and turn it into ASCII
        non_unicode_word = (unicodedata.normalize('NFKD', word).
            encode('ascii', 'ignore'))
        return filter(str.isalnum, non_unicode_word).lower()


# Augment the query.
def build_new_query(current_query, frequency_table):
    # Remove words in the current query as well as stop words, so that we do not
    # add them to the query.
    for word in current_query.split(' '):
        if word in frequency_table:
            del(frequency_table[word])
    for word in STOP_WORDS:
        if word in frequency_table:
            del(frequency_table[word])

    inverted_frequency_table = collections.defaultdict(list)
    for key, value in frequency_table.iteritems():
        inverted_frequency_table[value].append(key)

    words_by_frequency = []
    for count in sorted(inverted_frequency_table.keys(), reverse=True):
        words_by_frequency += inverted_frequency_table[count]

    # Augment by the two most frequent words.
    return '{} {} {}'.format(current_query, words_by_frequency[0],
                             words_by_frequency[1])


def main():
    # The first argument passed after the desired query string will be the
    # desired precision factor.
    precision = float(sys.argv[1])
    # The second argument passed after the python script name will be the
    # desired query.
    original_query = sys.argv[2]

    # Constants
    account_key_enc = base64.b64encode('{}:{}'.format(ACCOUNT_KEY, ACCOUNT_KEY))
    headers = {'Authorization': 'Basic {}'.format(account_key_enc)}
    # Cap the query cycle to 5 rounds
    max_queries = 5
    num_queries = 0

    precision_reached = False
    current_query = original_query


    print ('\nPARAMETERS\n'
           'Client key: {}\n'
           'Query: \'{}\'\n'
           'Precision: {}').format(
           ACCOUNT_KEY, original_query, precision)

    while not precision_reached and num_queries < max_queries:
        # Converts the user query string to HTML5 URL ready code.
        current_query_encoded = urllib.quote(current_query, safe='')
        req = urllib2.Request(BING_URL.format(current_query_encoded),
                              headers=headers)
        raw_response = urllib2.urlopen(req)

        num_queries += 1
  
        # Get responses, determine if they are relevant or not, and build the
        # frequency table
        all_responses = parse_xml(raw_response)
        relevant_responses, irrelevant_responses = (
            classify_responses(all_responses))
        frequency_table = build_frequency_table(
            relevant_responses, irrelevant_responses)

        actual_precision = round(
            len(relevant_responses) / len(all_responses), 2)

        print ('\n=========================\n\n'
               'FEEDBACK SUMMARY\n'
               'Query: \'{}\'\n'
               'Precision attained: {}\n'.format(
               current_query, actual_precision))

        # Augment the query using the frequency table
        current_query = build_new_query(current_query, frequency_table)

        # Check if the desired precision has been reached, and respond
        # appropriately. 
        if (actual_precision >= precision): 
            precision_reached = True
            print 'Desired precision of {} met!\n'.format(precision)
        elif (actual_precision < precision and num_queries == max_queries):
            print ('Precision unmet, but exceeded allowed query amount of {}.'
                   '\n'.format(max_queries))
        else:
            print 'Still below the desired precision of {}.'.format(precision)
            print 'Augmented query: \'{}\''.format(current_query)


if __name__=="__main__":
    main()