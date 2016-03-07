package feedback;

import java.io.IOException;
import java.io.InputStream;
import java.net.URL;
import java.net.URLConnection;
import java.net.URLEncoder;
import java.util.ArrayList;

import org.apache.commons.codec.binary.Base64;

import com.google.gson.Gson;

public class BingHelper {

	public static ArrayList<QueryResult> queryBing(String apiKey, String query) throws IOException {
		String bingUrl = "https://api.datamarket.azure.com/Bing/Search/Web?Query=%27"
				+ URLEncoder.encode(query, "UTF-8") + "%27&$top=10&$format=json";

		byte[] accountKeyBytes = Base64.encodeBase64((apiKey + ":" + apiKey).getBytes());
		String accountKeyEnc = new String(accountKeyBytes);

		URL url = new URL(bingUrl);
		URLConnection urlConnection = url.openConnection();
		urlConnection.setRequestProperty("Authorization", "Basic " + accountKeyEnc);

		InputStream inputStream = (InputStream) urlConnection.getContent();
		byte[] contentRaw = new byte[urlConnection.getContentLength()];
		inputStream.read(contentRaw);
		String content = new String(contentRaw);

		// The content string is the xml/json output from Bing.
		// System.out.println(content);

		Gson gson = new Gson();
		BingJson results = gson.fromJson(content, BingJson.class);

		return results.toQueryResults();
	}

	public class BingJson {
		BingJsonD d;

		public ArrayList<QueryResult> toQueryResults() {
			ArrayList<QueryResult> results = new ArrayList<QueryResult>(d.results.length);

			for (int i = 0; i < d.results.length; i++) {
				QueryResult r = new QueryResult();
				r.id = i;
				r.title = d.results[i].Title;
				r.description = d.results[i].Description;
				r.link = d.results[i].Url;

				results.add(r);
			}
			return results;
		}
	}

	public class BingJsonD {
		BingJsonResult[] results;
	}

	public class BingJsonResult {
		String ID;
		String Title;
		String Description;
		String Url;
	}
}
