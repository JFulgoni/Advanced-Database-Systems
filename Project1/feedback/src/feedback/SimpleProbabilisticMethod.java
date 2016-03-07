package feedback;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
import java.util.Map.Entry;
import java.util.PriorityQueue;
import java.util.TreeMap;

public class SimpleProbabilisticMethod implements RelevanceMethod{
	private Map<String, HashMap<Integer, ArrayList<TermMetadata>>> invertedIndex = new TreeMap<String, HashMap<Integer, ArrayList<TermMetadata>>>(String.CASE_INSENSITIVE_ORDER);

	@Override
	public String augmentQuery(ArrayList<QueryResult> documents, String query) {
		/*
		 * This function takes in as parameters a list of documents.
		 * and the query string.
		 * It returns an ArrayList<String> which contains the list of words to add to the next query.
		 */
		
		int numberOfDocuments = documents.size(); //this corresponds to our N value, should always be 10 here
		int numberOfRelevantDocuments = 0;
		
		// build inverted index
		for(int i = 0; i< numberOfDocuments; i++){
			QueryResult currentDocument = documents.get(i);
			
			PreprocessHelper.addDocumentToIndex(invertedIndex, currentDocument);
			
			if(currentDocument.isRelevant()){
				numberOfRelevantDocuments++; //this corresponds to our VR value
			}
		}
		
		PreprocessHelper.printIndexSummary(invertedIndex);

		
		PriorityQueue<TermScore> scoreHeap = new PriorityQueue<TermScore>();
		
		for (Iterator<Entry<String, HashMap<Integer, ArrayList<TermMetadata>>>> iter = invertedIndex.entrySet().iterator(); iter.hasNext();) {
			Entry<String, HashMap<Integer, ArrayList<TermMetadata>>> entry = iter.next();
			String term = entry.getKey();
			HashMap<Integer, ArrayList<TermMetadata>> docsWithTerm = entry.getValue();
			
			int docsTermAppearsIn = docsWithTerm.size(); //this corresponds to our DFt
			int relevantDocsTermAppearsIn = 0;
			
			for (Iterator<Entry<Integer, ArrayList<TermMetadata>>> docIter = docsWithTerm.entrySet().iterator(); docIter.hasNext();) {
				Entry<Integer, ArrayList<TermMetadata>> docEntry = docIter.next();
				
				int docId = docEntry.getKey();
				
				QueryResult currentDocument = documents.get(docId);
				if(currentDocument.isRelevant()){
					relevantDocsTermAppearsIn++; //this corresponds to our VRt
				}
			}
			
			//now we find our probability
			double probTermInRelevantDocs = (double) relevantDocsTermAppearsIn / numberOfRelevantDocuments;
			double probTermInNonRelevantDocs = (double) (docsTermAppearsIn - relevantDocsTermAppearsIn) / (numberOfDocuments - numberOfRelevantDocuments);
			double termProbability = probTermInRelevantDocs - probTermInNonRelevantDocs;
			
			TermScore score = new TermScore();
			score.score = termProbability;
			score.term = term;	
			scoreHeap.add(score);
		}
		
		TermScore best = scoreHeap.remove();
		TermScore second = scoreHeap.remove();
		
		System.out.println(best);
		System.out.println(second);
		while(!scoreHeap.isEmpty()) {
			System.out.println(scoreHeap.remove());
		}

		// append new terms to end of previous query
		StringBuilder buf = new StringBuilder();
		buf.append(query);
		buf.append(" " + best.term);
		buf.append(" " + second.term);
		
		return buf.toString();
	}

	
}
