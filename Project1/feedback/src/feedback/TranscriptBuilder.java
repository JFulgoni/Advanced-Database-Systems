package feedback;

import java.io.FileNotFoundException;
import java.io.PrintWriter;
import java.io.UnsupportedEncodingException;
import java.util.ArrayList;

public class TranscriptBuilder {
	
	private ArrayList<QueryResult> results;
	private PrintWriter writer;

	public TranscriptBuilder(){	
		try {
			writer = new PrintWriter("transcript.txt", "UTF-8");
		} catch (FileNotFoundException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (UnsupportedEncodingException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
	}
	
	public void setResults(ArrayList<QueryResult> results){
		this.results = results;
	}
	
	public void writeTranscript(int round, String query, float precision){
		writer.println("=====================================");
		writer.println("Round " + round);
		writer.println("Query '" + query + "'");
		
		for(int i = 0; i < results.size(); i++){
			QueryResult myResult = results.get(i);
			
			writer.println("\nResult " + (i + 1));
			
			if(myResult.isRelevant()){
				writer.println("Relevant: Yes");
			}
			else{
				writer.println("Relevant: No");
			}
			//navigate through each QueryResult object
			writer.println("[");
			writer.println(results.get(i));	
			writer.println("]\n");
		}	
		writer.println("Precision: " + precision);
	}
	
	public void closeWriter(){
		writer.close();
	}
	
}//end class
