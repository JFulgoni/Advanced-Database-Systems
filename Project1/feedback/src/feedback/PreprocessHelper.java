package feedback;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Set;

public class PreprocessHelper {
	// Stopwords originally from "http://www.ranks.nl/stopwords", further modified.
	public static final Set<String> STOPWORDS_SET = new HashSet<String>(Arrays.asList(
			"i", "a", "about", "and", "an", "are", "as", "at", 
			"be", "by", "com", "for", "from", "how", "in", 
			"is", "it", "of", "on", "or", "that", "the", 
			"this", "to", "was", "what", "when", "where",
			"who", "will", "with", "the", "www"
));
	
	public static String[] textToTerms(String myString) {
		/*
		 * This method takes a String, usually the title or the description
		 * given by a QueryResult object and returns an array of Strings that
		 * contain all of the individual words of the description.
		 */
		myString = myString.toLowerCase();
		myString = myString.trim();
		myString = myString.replaceAll("[^\\w\\s]", "");

		String[] myList = myString.split(" +");

		return myList;
	}
	
	public static  void addDocumentToIndex(Map<String, HashMap<Integer, ArrayList<TermMetadata>>> invertedIndex, QueryResult document) {
		addDocumentToIndexWithSection(invertedIndex, document, document.title, TermMetadata.Section.TITLE);
		addDocumentToIndexWithSection(invertedIndex, document, document.description, TermMetadata.Section.DESCRIPTION);
	}

	public static  void addDocumentToIndexWithSection(Map<String, HashMap<Integer, ArrayList<TermMetadata>>> invertedIndex, QueryResult document, String sectionText,
			TermMetadata.Section sectionType) {
		String[] terms = textToTerms(sectionText);
		for (int i = 0; i < terms.length; i++) {
			HashMap<Integer, ArrayList<TermMetadata>> termIndexList = invertedIndex.get(terms[i]);
			if (termIndexList == null) {
				termIndexList = new HashMap<Integer, ArrayList<TermMetadata>>();
				invertedIndex.put(terms[i], termIndexList);
			}

			ArrayList<TermMetadata> docIndexList = termIndexList.get(document.id);
			if (docIndexList == null) {
				docIndexList = new ArrayList<TermMetadata>();
				termIndexList.put(document.id, docIndexList);
			}

			TermMetadata metadata = new TermMetadata();
			metadata.document = document;
			metadata.section = sectionType;
			metadata.termPosition = i;

			docIndexList.add(metadata);
		}
	}

	public static void printIndexSummary(Map<String, HashMap<Integer, ArrayList<TermMetadata>>> invertedIndex) {
		for (Iterator<Entry<String, HashMap<Integer, ArrayList<TermMetadata>>>> iter = invertedIndex.entrySet()
				.iterator(); iter.hasNext();) {
			Entry<String, HashMap<Integer, ArrayList<TermMetadata>>> entry = iter.next();
			String term = entry.getKey();
			HashMap<Integer, ArrayList<TermMetadata>> docsWithTerm = entry.getValue();

			System.out.printf("Term '%s' is in %d documents\n", term, docsWithTerm.size());

			for (Iterator<Entry<Integer, ArrayList<TermMetadata>>> docIter = docsWithTerm.entrySet().iterator(); docIter
					.hasNext();) {
				Entry<Integer, ArrayList<TermMetadata>> docEntry = docIter.next();

				int docId = docEntry.getKey();
				ArrayList<TermMetadata> appearanceInDoc = docEntry.getValue();
				System.out.printf("\tDocument %d has term %d times\n", docId, appearanceInDoc.size());
			}

		}
	}
}
