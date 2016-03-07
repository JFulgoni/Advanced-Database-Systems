package feedback;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.Map.Entry;

import feedback.TermMetadata.Section;

import java.util.PriorityQueue;
import java.util.Set;

public class RelevantHigherWeightMethod implements RelevanceMethod {
	private HashMap<String, HashMap<Integer, ArrayList<TermMetadata>>> invertedIndex = new HashMap<String, HashMap<Integer, ArrayList<TermMetadata>>>();

	@Override
	public String augmentQuery(ArrayList<QueryResult> documents, String query) {
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
		Set<String> queryTerms = new HashSet<String>(Arrays.asList(PreprocessHelper.textToTerms(query)));
		
		for (Iterator<Entry<String, HashMap<Integer, ArrayList<TermMetadata>>>> iter = invertedIndex.entrySet().iterator(); iter.hasNext();) {
			Entry<String, HashMap<Integer, ArrayList<TermMetadata>>> entry = iter.next();
			String term = entry.getKey();
			HashMap<Integer, ArrayList<TermMetadata>> docsWithTerm = entry.getValue();
			
			if (queryTerms.contains(term)) {
				continue;
			}
			if (PreprocessHelper.STOPWORDS_SET.contains(term)) {
				continue;
			}
			
			int docsWithTermTotal = docsWithTerm.size(); //this corresponds to our DFt
			int relevantDocsWithTermTotal = 0;
			
			double boostFactor = 1;
			
			for (Iterator<Entry<Integer, ArrayList<TermMetadata>>> docIter = docsWithTerm.entrySet().iterator(); docIter.hasNext();) {
				Entry<Integer, ArrayList<TermMetadata>> docEntry = docIter.next();
				
				int docId = docEntry.getKey();
				ArrayList<TermMetadata> appearanceInDoc = docEntry.getValue();
				
				for (TermMetadata tm : appearanceInDoc) {
					if (tm.section == Section.TITLE) {
						boostFactor *= 1.1;
					}
				}
				
				QueryResult currentDocument = documents.get(docId);
				if(currentDocument.isRelevant()){
					relevantDocsWithTermTotal++; //this corresponds to our VRt
				}
			}
			
			//now we find our probability
			double probTermInRelevantDocs = (double) relevantDocsWithTermTotal / numberOfRelevantDocuments;
			double probTermInNonRelevantDocs = (double) (docsWithTermTotal - relevantDocsWithTermTotal) / (numberOfDocuments - numberOfRelevantDocuments);
			double termProbability = probTermInRelevantDocs*5 - probTermInNonRelevantDocs;
			
			TermScore score = new TermScore();
			score.score = termProbability * boostFactor;
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
