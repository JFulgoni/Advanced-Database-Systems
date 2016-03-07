John Fulgoni jsf2154
David Ding dwd2112

=======================
List of files:

hw2.py - python file used to run our project

*.txt - various .txt files given by professor to act as queries for the system

README.txt - this file

=======================
How to run:

Simply type into the command line:
python hw2.py <t_es> <t_ec> <host>

==========================
Part 1 Design:

We first set up the .txt files for later querying. We take the txt file, and append each query to an appropriate query list.

Starting with the root query list, we iterate through the list and query bing for its results using our query_bing function.
From this, we return a score vector which serves as our Coverage Vector.
We then convert our Coverage vector to a Specificity Vector.

We then send both our Coverage and Specificity Vectors to a classify_vector function, which returns a 3x1 vector.
This matrix contains all of the classifications that match the thresholds provided.

We then iterate through the classification vector, and if there is a 1 in the proper column, we then query Bing again using the leaf node queries (computers, health, sports).
We process the classify vector for this second tier, and make a 3x2 matrix with all possible classifications.

We take this depth matrix, and send it to our get_result function, where it returns a string based on the contents of the matrix.
If there is a -1 in a row (either col), then we know that the higher level wasn't classified (computers, health, sports).
If there is a 1 in a given row and col, we know that we can classify as a subcategory (ex. Diseases and Fitness).
If there is a 0 in a given row and col, that means we have the main category (Health), but not subcategory (Disease or Fitness).
This function returns the proper string of classification of the host.

======================
Part 2a Design:

In the query_bing function, we return the number of results in a query, as well as the first four returned urls.
We use the parse_xml function to return the URL from the XML transaction.

========================
Part 2b Design:

Once we have the list of URLs, we can pass the list to the lynx_dict function, which returns a dictionary of words that exist in the pages.

For each URL in the list, we use our lynx_dump function, which calls the 'lynx --dump' command from the os in order to get the raw data from the page.
We chose to ignore URLs that lead to .pdf files in our implementation.

We then send that raw data to the process_lynx function which returns a list of words that appear in the document.
The process_lynx function first uses regular expressions to get rid of any text inside of square braces.
After that, we use python's .split() function to take the text and transform it into a list of words.
We send that list of words to our clean_words function, which only keeps words that contain alphabetic characters, and removes punctuation.
Once we have the cleaned list of words, we update our dictionary for all of the URLs.

We can use the lynx_dict function for the root as well as available subcategories.
We process the root dictionary first, and keep it by itself.
For each subcategory that the query is classified as, we then use the lynx_dict function to make a dictionary, and add each one to a list of dictionaries.

Once we have the list of subcategory dictionaries, we write each of them to its own file, and then merge it with the root dictionary.
When all of the subcategories have been added to the root, we can write the root dictionary to its own file.
The write_to_file function takes in the string classification and the host domain, and writes the dictionary and its values to a file.

==========================
Bing search account keys:
XuOLiXL26shewnIRN64uXZ339idWvzPDLOK6u022udM
cKO631x6HcoJ4E9Vcu0vGsUF3ND1q2pwf1hzdTjgcKE
