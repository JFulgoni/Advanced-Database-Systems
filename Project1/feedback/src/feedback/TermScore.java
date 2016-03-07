package feedback;

public class TermScore implements Comparable<TermScore> {
	String term;
	double score;
	
	@Override
	public int compareTo(TermScore o) {
		double temp = this.score - o.score;
		if (temp > 0) {
			return -1;
		} else if (temp == 0) {
			return 0;
		} else {
			return 1;
		}
	}

	@Override
	public String toString() {
		return "term=" + term + ", score=" + score;
	}
	

	
	
}
