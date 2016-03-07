Project 3

a. Members: John Fulgoni (jsf2154), John Chung (jjc2254)

b. Files for submission:
  hw3.py, create_dataset.py, README.txt, example-run.txt, INTEGRATED-DATASET.csv
  Civil_List_2014.csv

c. Description of our INTEGRATED-DATASET.csv file.
  (1) We are using the "Civil List 2014" dataset provided by nycopendata.com.
    The description of the data per nycopendata.com reads as follows:

    The Civil List reports the agency code (DPT), first initial and last name (NAME),
    agency name (ADDRESS), title code (TTL #), pay class (PC), and salary (SAL-RATE)
    of individuals who were employed by the City of New York at any given time during the indicated year.

  (2) Procedure used to map the original open data set into our INTEGRATED-DATASET:
    To convert the Civil_List_2014.csv file into our INTEGRATED-DATASET, we run the python script create_dataset.py.
    To run:
    python create_dataset.py <dataset.csv>
    <dataset.csv> in this case is Civil_List_2014.csv

    We only take in the first 50K lines of the csv file (the whole doc is ~280K) for the sake of processing time.
    We believe this should be ok, since the data is sorted alphabetically by name, that the assumption should be a pretty even distribution between departments, salaries, and names.

    We first take the SAL-RATE column (formatted as '$50,000.00') and remove the punctuation.
    After that, we divide the value by 10k, which returns the number value in the ten-thousands place.
    We replace the SAL-RATE column with this value, which makes each salary in a $10K range, instead of being very specific numbers.
    In addition, if the salary is above $50K, we add a column which says if their salary is above or below $50K.
    ($50K is treated as below $50K, since it is not greater)

    Afterwards all the processing, we remove the Agency Code, Name, and Pay Class columns.
    Since these are all very specific values, we decide to remove them for the sake of providing meaningful relationships.

    Our final row entry in INTEGRATED-DATASET resembles keys as follows:
    (ADDRESS, TTL CODE, SALARY, ABOVE/BELOW 50K)

  (3) What makes our INTEGRATED-DATASET interesting:
    Our dataset is interesting because it provides an insight to which civil service jobs pay what salary,
    as well as insight as to which departments pay more than others.
    We're able to see which title codes correspond to which pay ranges, and if they make over or under $50K a year.
    We can also see which departments pay the most, or pay the least.


d. How to run our program:

  python hw3.py INTEGRATED-DATASET.csv <minSupport> <minConfidence>
  <minSupport> & <minConfidence> should be digits between 0 and 1 (ex: 0.5)

e. Internal design of project:
  We have written our project code in a functional style using python 2.7.
  The set of functions include AprioriAlgo, candidateGeneration, outputResults,
  write_to_file, contained, iterateCSV, main. We wrote the a priori algorithm as
  described in the Argawal paper section 2.1. The major work is done in the AprioriAlgo and candidateGeneration functions
  while the other functions perform auxiliary tasks.

  Instead of using a hash-tree to store subsets in the 'prune' stage
  as outlined in section 2.1.2 of the paper, however, we store subsets for each permutation in a list of tuples (currentLarge)
  and prune to return only the subsets that have items above minimum support threshold. Pruning is done by sending subset list of tuples
  to the candidateGeneration function which only returns a list of subsets that are above threshold. We then revise currentLarge
  and store the qualifying subsets in a dictionary (largeSet).

  In our main function we begin by loading all the values of the INTEGRATED-DATASET into a list of rows using our iterateCSV function.
  We then go through this data row by row, and convert it to a list of lists.
  The list allTransactions contains a list of lists, where the first list is a row in the csv file, and each sub list is a list of items.
  The list allItems is a list where each item in the list is an item from each transaction, making this a list of every market basket item that appears.
  We pass both of these lists to the AprioriAlgo function, along with the minimum support and confidence level constants.

  The first thing we do in the AprioriAlgo is to create the candidateset using the candidateGeneration function.
  This function takes in the allTransaction and allItems list, and returns a list of frequent items.
  The function iterates through each item in allItems, and if the item is in a transaction, we increment that items' count.
  If the count of that item over the total number of transactions, it has a good enough support value, and can be considered a candidate.
  In order for our version of the subset function to work, we need to have a data structure that stores all list of items (individual words) in a given transaction
  that exceed the minimum support level according to their transaction ID. We do exactly that by using the largeOne dictionary and storing candidate items in one
  sorted by transaction ID. This way, we will have candidate items sorted in order so we can use Python's itertools.combinations built-in function to
  generate subset permutations in order thus avoiding duplicates rule associations (ex. a==>b, b==>a). So, we iterate through all items in each transaction and
  compare them to the candidateset that has all candidate items above minimum support. If the item is in the candidateset, we store it in a list and then
  to the dictionary with the transaction ID being the key.

  We then iterate through the largeOne dictionary k times, where k is the size of a row in our dataset.
  In our case, the size of the rows never change, so we only have to iterate through the following loop 4 times.
  With each iteration, we use iteritools.combinations to create all possible combinations of item sets of the current k size.
  For instance, a combination of k = 3 could be:
  	(['POLICE DEPARTMENT', '$70K', 'Above 50K'])

  We then set the currentLarge list to a list of tuples for each row in the subset list (subsetList).
  Once we have the currentLarge list, we then create a new set of candidates using the candidateGeneration function, this time using the new currentLarge set.
  The currentLarge set variable exists to keep track of the process.
  We then store the newly permuted subsets that are above minimum support in a dictionary (largeSet) of lists with the row number ('k') being the dictionary ID.

  After we have iterated through the lists of all possible combinations, we create a list of items above minimum support and association
  rules above minimum confidence. To create the list of frequent items, we iterate through each item in the largeSet dictionary and add it to the generateItems list along with its
  support level. Since all items in largeSet are above minimum support, we can simply add each item without checking its support level.
  To create the list of rules, we have to make sure the confidence level of the association rule is above threshold.
  If any subset in the largeSet list has a confidence level above minimum confidence and the association rule has two items, we add it to the list of rules
  along with its support and confidence level. Since items in largeSet were only vetted for support levels, we have to do the confidence level calculation at this stage.
  Once we have added all working subsets to the list generateRules, we can return both generateRules and generateItems to the main function.

  After we return our items and rules, we then use outputResults and write_to_tile to show the results.
  Both of these functions are nearly identical: outputResults just returns the formatted results to the command line,
  while write_to_file takes the same results and writes them to output.txt

f. Interesting sample run:

  python hw3.py INTEGRATED-DATASET.csv 0.01 0.42

  While we can see that certain pairings are obviously correlated (60K implies Over 50K), there are many interesting relations.
  The 50K distinction was based on observation of the data and is arbitrary.
  We can even see right away that there are more jobs offered by the city that are paid under 50K than over 50K:
  ['Below 50K'] , 52.29%
  ['Above 50K'] , 47.71%
  We see the 70K salary range to be more common among salaries above 50K while 00K is more common among salaries below 50K.
  When we investigate further the 00K salaries are actually hourly rates.
  ['$70K'] , 18.18%
  ['$70K', 'Above 50K'] , 18.18%
  ['$00K'] , 16.58%
  ['$00K', 'Below 50K'] , 16.58%

  For instance, CUNY Community Colleges seem to have a tendency to pay employees under $50K:
  ['CUNY KINGSBOROUGH COMMMUNI'] ==> ['Below 50K'] (Conf: 93.54% , Supp: 1.16%)
  ['CUNY LAGUARDIA COMMUNITY C'] ==> ['Below 50K'] (Conf: 87.80% , Supp: 1.11%)
  ['CUNY MANHATTAN COMMUNITY C'] ==> ['Below 50K'] (Conf: 86.06% , Supp: 1.00%)

  Departments that pay Over 50K include the Fire Department, Police Department, N.Y.C. TRANSIT AUTHORITY
  the Department of Corrections, and Sanitation.
  ['FIRE DEPARTMENT'] ==> ['Above 50K'] (Conf: 64.88% , Supp: 3.56%)
  ['POLICE DEPARTMENT'] ==> ['Above 50K'] (Conf: 52.39% , Supp: 9.99%)
  ['N.Y.C. TRANSIT AUTHORITY'] ==> ['Above 50K'] (Conf: 78.40% , Supp: 16.42%)
  ['DEPARTMENT OF SANITATION'] ==> ['Above 50K'] (Conf: 64.57% , Supp: 2.32%)

  Departments that pay below 50K (00K hourly wage observations not included) include the the following departments:
  ['CUNY KINGSBOROUGH COMMMUNI'] ==> ['Below 50K'] (Conf: 93.54% , Supp: 1.16%)
  ['CUNY LAGUARDIA COMMUNITY C'] ==> ['Below 50K'] (Conf: 87.80% , Supp: 1.11%)
  ['CUNY MANHATTAN COMMUNITY C'] ==> ['Below 50K'] (Conf: 86.06% , Supp: 1.00%)
  ['DEPARTMENT OF CITYWIDE ADM'] ==> ['Below 50K'] (Conf: 96.27% , Supp: 5.42%)
  ['N.Y.C. HOUSING AUTHORITY'] ==> ['Below 50K'] (Conf: 82.89% , Supp: 3.51%)
  ['DEPARTMENT OF TRANSPORTATI'] ==> ['Below 50K'] (Conf: 73.13% , Supp: 1.31%)
  ['ADMINISTRATION FOR CHILDRE'] ==> ['Below 50K'] (Conf: 66.98% , Supp: 1.57%)
  ['DEPARTMENT OF ENVIRONMENTA'] ==> ['Below 50K'] (Conf: 65.79% , Supp: 1.31%)
  ['DEPARTMENT OF HEALTH AND M'] ==> ['Below 50K'] (Conf: 65.78% , Supp: 1.39%)
  ['DEPARTMENT OF EDUCATION'] ==> ['Below 50K'] (Conf: 59.84% , Supp: 2.65%)

  It's implied that most of the Department of Parks and Rec, the Department of citywide administration employees are not salary based but hourly wage employees.
  ['DEPARTMENT OF PARKS & RECR'] ==> ['$00K', 'Below 50K'] (Conf: 50.08% , Supp: 1.29%)
  ['DEPARTMENT OF CITYWIDE ADM'] ==> ['$00K'] (Conf: 88.99% , Supp: 5.01%)

  We can also see where certain job titles come together with departments and pay.
  Here, we can see that the title 70310 has a high frequency with the fire department, and that 70310 also implies a salary of 70k.
  ['FIRE DEPARTMENT', '70310'] , 2.60%
  ['70310'] ==> ['$70K'] (Conf: 85.08% , Supp: 2.21%)

  The job titles 10209, 12702 and 10102 seem most likely associated with hourly wage employees.
  ['10209'] ==> ['$00K'] (Conf: 100.00% , Supp: 1.75%)
  ['12702'] ==> ['$00K'] (Conf: 100.00% , Supp: 3.27%)
  ['10102'] ==> ['$00K'] (Conf: 100.00% , Supp: 1.51%)

  By analyzing this data, we can continue to make implications between salaries and departments in NYC.

g. Additional information:

  Although not required to submit any code or scripts used to generate the INTEGRATED-DATASET file,
  we include our script (creat_dataset) for reference purposes only.
  Also, instead using a hash-tree to delete all item sets that are not a subset of the initial
  candidate k-item sets in the 'prune step', we store subsets in a list of tuples and iteratively prune as described in part e of our README file.
