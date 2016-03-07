package feedback;

public class TermMetadata {
	public QueryResult document;

	public int termPosition;
	public Section section;
	
	public enum Section {
	    TITLE,
	    DESCRIPTION,
	}
}
