'''
python2 hw3.py INTEGRATED-DATASET.csv <minSupport> <minConfidence>
<minSupport> & <minConfidence> are should be digits between 0 and 1
'''

import sys
import collections
import itertools

# A priori algorith as outlined in the paper by Agrawal section 2.1
def AprioriAlgo(allTransactions, allItems, minSupp, minConf):
    # setCount stores the frequency for each given item. Items will be tuples to allow for hashing
    # largeOne stores the candidate items with the key being the transaction ID. This will preserve order when permuting subsets
    # largeSet will
    setCount = collections.defaultdict(int)
    largeOne = dict()
    largeSet = dict()
    candidateset = candidateGeneration(allTransactions,allItems,minSupp,setCount)
    currentLarge = candidateset
    TID = 0
    transLen = 0
    for item in allTransactions:
        orderedCand = list()
        transLen = len(item)
        TID = 1 + TID
        for word in item:
            for candidate in currentLarge:
                if word in candidate:
                    orderedCand.append(word)
                largeOne[TID] = orderedCand
    # We generate all possible subsets for {large itemsets} and store them in subsetList.
    # We then 'prune' the subsetList using the candidateGenerate function and return subsets that only exceed the minSupp threshold
    # Pruned subset list is then stored in the largeSet dictionary with the transaction column ID being the key of the dictionary
    # The while loop continues until we reach the total number of transaction columns which will be uniform in our case
    k = 1
    while(k < transLen + 1):
        subsetList = list()
        for key, value in largeOne.items():
            for subset in itertools.combinations(value, k):
                subsetList.append(subset)
        currentLarge = [tuple(row) for row in subsetList]
        currentCandidate = candidateGeneration(allTransactions,currentLarge,minSupp,setCount)
        currentLarge = currentCandidate
        largeSet[k] = currentLarge
        k = k + 1
    # We generate a list of tuples within a list that stores the candidate items and their support level
    generateItems = []
    for key, value in largeSet.items():
        for item in value:
            generateItems.extend([(list(item), float(setCount[item])/len(allTransactions))])
    # We generate a list of tuples within a list that stores qualifiying association rules along with the confidence and support levels
    generateRules = []
    for key, value in largeSet.items():
        for item in value:
            support = float(setCount[item])/len(allTransactions)
            confidence = (float(setCount[item])/len(allTransactions))/(float(setCount[item[0]])/len(allTransactions))
            if (confidence >= minConf) and (list(item[1:])):
                generateRules.append((([item[0]], list(item[1:])),confidence, support))
    return generateItems, generateRules
# This function checks whether a list is a subset of another list. This is mainly used by the candidateGeneration function
def contained(candidate, container):
    temp = container[:]
    try:
        for c in candidate:
            temp.remove(c)
        return True
    except ValueError:
        return False
# This function generates candidate items that are above minSupp threshold and returns in a list form
def candidateGeneration(allTransactions, allItems, minSupp, setCount):
        # newCandidate stores new subsets and localSet keeps track of subsets and their frequency
        newCandidate = list()
        localSet = collections.defaultdict(int)
        # iterate through allItems list(set(allItems) will ensure duplicates are removed
        for item in list(set(allItems)):
            for transaction in allTransactions:
                if (item in transaction) or contained(item, transaction):
                    setCount[item] += 1
                    localSet[item] += 1
        # Add candidate items above minSupp to the newCandidate list
        for item, count in localSet.items():
                support = float(count)/len(allTransactions)
                if support >= minSupp:
                        newCandidate.append(item)

        return newCandidate
# This function gets rid of any whitespace or trailing commas that might have carried forward
def iterateCSV(csvfile):
        csvreader = open(csvfile, 'rU')
        for line in csvreader:
                line = line.strip().rstrip(',')
                record = list(line.split(','))
                yield record
# This function outputs results per Project 3 instructions on COMS W6111 website
def outputResults(items, rules, minSupp, minConf):
    print "\n==Frequent itemsets (min_sup = %.2f%%" % (minSupp*100) + ")"
    for item, support in sorted(items, key=lambda (item, support): support, reverse =True):
        print "%s , %.2f%%" % (str(item), support*100)
    print "\n==High-confidence association rules (min_conf= %.2f%%" % (minConf*100) + ")"
    for rule, confidence, support in sorted(rules, key=lambda (rule, confidence, support): confidence, reverse =True):
        lhs, rhs = rule
        print "%s ==> %s" % (str(lhs), str(rhs)) + " (Conf: %.2f%% " % (confidence*100) + ", Supp: %.2f%%)" % (support*100)
    print "\n"

# This function does outputs the same information as the function outputResults, and writes them a file
def write_to_file(items, rules, minSupp, minConf, filename):
    my_file = open(filename, 'w')
    my_file.write("\n==Frequent itemsets (min_sup = %.2f%%" % (minSupp*100) + ")\n")
    for item, support in sorted(items, key=lambda (item, support): support, reverse =True):
        my_file.write("%s , %.2f%%\n" % (str(item), support*100))
    my_file.write("\n==High-confidence association rules (min_conf= %.2f%%" % (minConf*100) + ")\n")
    for rule, confidence, support in sorted(rules, key=lambda (rule, confidence, support): confidence, reverse =True):
        lhs, rhs = rule
        my_file.write("%s ==> %s" % (str(lhs), str(rhs)) + " (Conf: %.2f%% " % (confidence*100) + ", Supp: %.2f%%)\n" % (support*100))
    my_file.close()

def main():
    # Read in file and get a generator using itertools
    dataFile = iterateCSV(sys.argv[1])
    allTransactions = list()
    allItems = list()
    for record in dataFile:
        transaction = list(record)
        allTransactions.append(transaction)
        for item in transaction:
            allItems.append(item)
    minSupp = float(sys.argv[2])
    minConf = float(sys.argv[3])
    items, rules = AprioriAlgo(allTransactions, allItems, minSupp, minConf)
    # output results to display as well as to a file named 'output.txt' per hw instructions
    outputResults(items, rules, minSupp, minConf)
    write_to_file(items, rules, minSupp, minConf, 'output.txt')

if __name__=="__main__":
    main()
