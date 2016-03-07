package feedback;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.regex.Pattern;

public class UserInterface {
	
	public static RelevanceMethod method = new PlaygroundMethod();

	public static void main(String[] args) throws IOException {
		boolean isValid = args.length == 3 && isDouble(args[1]);
		if (!isValid) {
			System.out.println("Usage: executable bing_key precision 'query'");
			System.out.printf("Got: %s", Arrays.deepToString(args));
			System.exit(1);
		}

		String bingApiKey = args[0];
		double precision = Double.parseDouble(args[1]);
		String query = args[2];

		System.out.printf("Bing Key: '%s'\n", bingApiKey);
		System.out.printf("Precision: %f\n", precision);
		System.out.println("Query: " + query);
		System.out.println("--------------------------");
		
		TranscriptBuilder transcriptBuilder = new TranscriptBuilder();
		int round_counter = 0;

		double lastPrecision = 0;
		while (true) {
			ArrayList<QueryResult> results = BingHelper.queryBing(bingApiKey, query);

			if (results.size() != 10) {
				System.out.printf("Bing returned %d results, expected 10\n", results.size());
				return;
			}

			requestRelevanceFeedback(results);

			int numberOfRelevantDocuments = 0;
			for (QueryResult result : results) {
				if (result.isRelevant) {
					numberOfRelevantDocuments++;
				}
			}
			if (numberOfRelevantDocuments == 0) {
				System.out.println("No results are relevant, finished processing");
				break;
			}
			if (lastPrecision != 0 && lastPrecision >= precision) {
				System.out.println("No improvement compared to last round. Exiting...");
				break;
			}
			float currentPrecision = (float) numberOfRelevantDocuments / (float) results.size();
			
			//experiment with this Transcript Builder
			transcriptBuilder.setResults(results);
			transcriptBuilder.writeTranscript(++round_counter, query, currentPrecision);
			
			if (currentPrecision >= precision) {
				System.out.printf("Achieved precision goal: %f. Exiting...", currentPrecision);
				break;
			}
			lastPrecision = currentPrecision;
			

			query = method.augmentQuery(results, query);

			System.out.println("New query: " + query);
		}
		transcriptBuilder.closeWriter();
	}

	public static void requestRelevanceFeedback(ArrayList<QueryResult> results) throws IOException {
		BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
		
		for (QueryResult result : results) {
			System.out.println(result);

			while (true) {
				System.out.println("Relevant? (y/n)");
				String input = br.readLine().trim();
				if (input.startsWith("y")) {
					result.setRelevant(true);
					break;
				} else if (input.startsWith("n")) {
					result.setRelevant(false);
					break;
				} else {
					System.out.println("Failed to read input. Try again:");
				}
			}
		}
	}

	// code copied from Java library docs:
	// https://docs.oracle.com/javase/6/docs/api/java/lang/Double.html#valueOf%28java.lang.String%29
	public static boolean isDouble(String a) {
		final String Digits = "(\\p{Digit}+)";
		final String HexDigits = "(\\p{XDigit}+)";
		// an exponent is 'e' or 'E' followed by an optionally
		// signed decimal integer.
		final String Exp = "[eE][+-]?" + Digits;
		final String fpRegex = ("[\\x00-\\x20]*" + // Optional leading
													// "whitespace"
		"[+-]?(" + // Optional sign character
				"NaN|" + // "NaN" string
				"Infinity|" + // "Infinity" string

		// A decimal floating-point string representing a finite positive
		// number without a leading sign has at most five basic pieces:
		// Digits . Digits ExponentPart FloatTypeSuffix
		//
		// Since this method allows integer-only strings as input
		// in addition to strings of floating-point literals, the
		// two sub-patterns below are simplifications of the grammar
		// productions from the Java Language Specification, 2nd
		// edition, section 3.10.2.

		// Digits ._opt Digits_opt ExponentPart_opt FloatTypeSuffix_opt
		"(((" + Digits + "(\\.)?(" + Digits + "?)(" + Exp + ")?)|" +

		// . Digits ExponentPart_opt FloatTypeSuffix_opt
				"(\\.(" + Digits + ")(" + Exp + ")?)|" +

		// Hexadecimal strings
				"((" +
				// 0[xX] HexDigits ._opt BinaryExponent FloatTypeSuffix_opt
				"(0[xX]" + HexDigits + "(\\.)?)|" +

		// 0[xX] HexDigits_opt . HexDigits BinaryExponent FloatTypeSuffix_opt
				"(0[xX]" + HexDigits + "?(\\.)" + HexDigits + ")" +

		")[pP][+-]?" + Digits + "))" + "[fFdD]?))" + "[\\x00-\\x20]*");// Optional
																		// trailing
																		// "whitespace"

		if (Pattern.matches(fpRegex, a)) {
			return true;
		}

		return false;
	}
}
