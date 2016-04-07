John Fulgoni jsf2154
Mateus Braga ma3382

=====================
List of files:

jsf2154_ma3382_hw1.jar - .jar file to run in our command line
transcript_* - different transcript outputs for required query submissions.

UserInterface.java - takes Bing key, Precision, and Query and retrieves QueryResults from Bing. Takes updated query information and loops again through Bing Queries.

BingHelper.java - does all of I/O stuff regarding Bing and JSON queries and results.

QueryResult.java - Data Structure for receiving queries from Bing. Each QueryResult has the title, link, and description from Bing results.

PreprocessHelper.java - Took either the Title or Description field of a QueryResult, and returned an ArrayList of Strings with all of the words separated. Removed punctuation, special characters, and stop words from the field, so that the query 

RelevanceMethod.java - interface for various methods that we tried.

SimpleProbabilisticMethod.java - method for deciding on the next two words to be added to the query. Used the Rocchio Algorithm to compare probability words in relevant documents vs words in non-relevant documents.

RelevantHigherWeightMethod.java - general improvement to the above “simple” model. Added weighting of words, as well as implementation of the PreprocessHelper class.

TermMetadata.java - data stucture for holding all the information about a term in question. This refers to any specific instance of a term in any document. Holds information such as position, and section of where the term was found within a document.

TermScore.java - data structure holding the score of each term. Compared scores of various terms in order to decide which term to use using a Priority Queue.

PlaygroundMethod.java - a third class that implements RelevanceMethod, but in addition to other features, is based on the frequency of words within a field, and gives a multiplier to the score accordingly.

TranscriptBuilder.java - class that writes the transcript file. Built to imitate the transcript.txt that we received from the reference implementation. Also returns results to ’transcript.txt’

==================================
How to run:
Included, we have jsf2154_ma3382_hw1.jar
To run, simply type into your command line:

java -jar jsf2154_ma3382_hw1.jar XuOLiXL26shewnIRN64uXZ339idWvzPDLOK6u022udM 0.9 ‘<QUERY HERE>’

=====================================
Description of Design:

In our project, we start with the User Interface class, which acts as our main function. We then get the arguments from the user.

With the Bing Key and Query, we make an instance of BingHelper class and retrieve a set of results, which we format into an ArrayList of QueryResult objects.

From the list of QueryResults, we then ask the users through the command line to mark documents as relevant.

If the precision is met, then the program terminates. If the precision doesn’t improve or is 0, then we also terminate. If the precision is somewhere in the middle, we continue with the program.

Once the documents are marked, then the PlaygroundMethod class object will decide which two words to append to the query.

Within our PlaygroundMethod class, we first process the strings using the PreprocessHelper class. This removes all of the special characters and stop words from the field, and gathers specific information about the terms. This information is stored in TermMetadata class.

The PlaygroundMethod then makes its judgment about words after scoring them all (explained in detail in the next section), appends the two words to the query, and returns it to the user interface.

The user interface then runs through the main loop again - querying Bing with the new query, making the user mark documents as relevant, and deciding once again if it should terminate, or let the Playground Method continue.

Through each UserInterface loop, our TranscriptBuilder class keeps track of all the information in a given round, and outputs it to ‘transcript.txt’. Note that the program must terminate before the text file is written.

====================================
Description of Query-Modification Method.

We originally started out with our RelevanceMethod interface, and a SimpleProbabilisticMethod approach to finding the best words for the query. This process took a basic approach to choosing the words.

First the title and description fields were processed into ArrayLists of words. We removed all the special characters, made each word lower case, and also removed all of the stop words. We found that stop words were filtered away most of the time by the core function, but in cases like ‘Taj Mahal’, ‘who’ was repeatedly chosen because of its uniqueness to the man, not the natural wonder.

Our original approach dealt with comparing probabilities of the words in relevant documents vs words in non-relevant documents:

Steps:
1. We took the number of relevant documents a term was in, and divided it by the total number of relevant documents. For this, we wanted to see the percentage of relevant documents the term appeared in. (Let’s call this number A)
2. We took the difference of how many times the term appeared in non-relevant docs vs relevant docs, and divided that number by the total number of non-relevant docs. (Let’s call this number B)
3. We then subtracted these two calculations, and this probability was used as the score to compare terms. Terms that appeared in relevant documents, and didn’t appear in non-relevant documents, would have the highest scores.

The terms with scores were all put in a priority queue, and once the queue was finished being built, the top two terms of the queue would be the ones we append to the query. Note that they would be appended in order of the score, Best + Second Best.

SimpleProbabilisticMethod:	Score = A - B

Based on this, we made a second approach in our RelevantHigherWeightMethod class, which made some improvements to the simple approach.

In RelevantHigherWeightMethod, instead of subtracting the two calculations found in steps 1. and 2., we first multiple the number in step 1. by 5. The reason we did this, is that we wanted to show that words in relevant documents were still worth more even if they appeared in non-relevant documents.

In addition, we also decided that if a term appeared in the title (relevant or not), we would give it a boost factor of 10%. That way, we would know that that particular term has some more meaning, and we should let it shine.

RelevantHigherWeightMethod: 	Score = boost*(5A - B)

For our third approach, we decided to try something a little different. In our PlaygroundMethod class, we used many of the same approaches as above (preprocessing, weighting words in the title), our scores were now based on the frequency of the term in a particular QueryResult.

Since we had all of this TermMetadata saved, and were able to calculate the number of times each term appears in each document, we decided to base our score on that. Not only would the best terms be unique to relevant docs, but they would appear in those documents more frequently.

We kept a running cumulative score for each term, giving a +1 if the term appeared in the description, and +1.15 if the term appeared in the title. We then multiplied this number by a factor based on how many documents the term appears in.

If the document was relevant, then this calculation was multiplied by three, then added to the cumulative score, otherwise the score was subtracted from the cumulative score. By doing this, we still kept the same general approach as before (weighting terms in the title, giving more weight to terms in relevant docs), but adjusted it for the frequency calculations.

Each term would be added to the priority queue as before, and the two leading terms at the end were chosen to be added to the query.

PlaygroundMethod:	If relevant ->	Cumulative score += frequency * term score * 3
			Else ->		Cumulative score -= frequency * term score

==========================
Bing search account key:

XuOLiXL26shewnIRN64uXZ339idWvzPDLOK6u022udM

=========================
Other information:

Even though we tried several approaches, we believed each one worked in one sense or another. We believe that most of this (just like real life search engines) comes down to personal preference, and also a personal definition of what documents are relevant.

This project was developed using the eclipse IDE