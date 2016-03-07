package feedback;

import java.util.ArrayList;

public interface RelevanceMethod {
	public String augmentQuery(ArrayList<QueryResult> documents, String query);
}
