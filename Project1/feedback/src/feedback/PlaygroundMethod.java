package feedback;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.PriorityQueue;
import java.util.Set;
import java.util.Map.Entry;

import feedback.TermMetadata.Section;

public class PlaygroundMethod implements RelevanceMethod {
	private HashMap<String, HashMap<Integer, ArrayList<TermMetadata>>> invertedIndex = new HashMap<String, HashMap<Integer, ArrayList<TermMetadata>>>();

	@Override
	public String augmentQuery(ArrayList<QueryResult> documents, String query) {
		int relevantDocumentsTotal = 0;
		
		// build inverted index
		for(int i = 0; i< documents.size(); i++){
			QueryResult currentDocument = documents.get(i);
			
			PreprocessHelper.addDocumentToIndex(invertedIndex, currentDocument);
			
			if(currentDocument.isRelevant()){
				relevantDocumentsTotal++; //this corresponds to our VR value
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
			
			double documentFreqFactor = Math.log10(documents.size()/docsWithTermTotal);
			double cumTermScore = 0;
			
			for (Iterator<Entry<Integer, ArrayList<TermMetadata>>> docIter = docsWithTerm.entrySet().iterator(); docIter.hasNext();) {
				Entry<Integer, ArrayList<TermMetadata>> docEntry = docIter.next();
				int docId = docEntry.getKey();
				ArrayList<TermMetadata> appearanceInDoc = docEntry.getValue();
				
				double score = 0;
				for (TermMetadata tm : appearanceInDoc) {
					if (tm.section == Section.TITLE) {
						score += 1.15;
					} else {
						score += 1;
					}
				}
				
				QueryResult currentDocument = documents.get(docId);
				if(currentDocument.isRelevant()){
					relevantDocsWithTermTotal++; //this corresponds to our VRt
					cumTermScore += score*documentFreqFactor*3;
				} else {
					cumTermScore -= score*documentFreqFactor;
				}
			}
			
			TermScore score = new TermScore();
			score.score = cumTermScore;
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
