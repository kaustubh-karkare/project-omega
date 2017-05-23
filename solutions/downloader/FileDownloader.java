/**
  * This is the Thread which initiates the downloading process.
  * The URL is verified. If succeeded, then host, port and path are extracted from the URL.
  * Content length and status code is obtained from the server.
  * If download is possible, multiple threads are used to download the file simultaneously.
  * Each thread is responsible for downloading a part of the file.
  */
package downloader;

import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.MalformedURLException;
import java.net.Socket;
import java.util.regex.Pattern;
import java.util.regex.Matcher;
import java.util.logging.Logger;
import java.util.LinkedHashMap;
import java.util.Map;

class URLInfo {
	String host;
	String fileName;
	String filePath;
	int port;
}

public class FileDownloader extends Thread {
	private final static Logger logger =
		Logger.getLogger(FileDownloader.class.getName());
	private final static String NEW_LINE = "\r\n";
	private Socket socket;
	private int contentLength;
	private int statusCode;
	private int threadCount;
	private DownloadThread downloadThreads[];
	private String verifiedURL;
	private URLInfo urlInfo;
	private BufferedReader inFromServer = null;
	private DataOutputStream outToServer = null;

	public FileDownloader(String url, int threadCount) {
		urlInfo = new URLInfo();
		this.threadCount = threadCount;

		verifiedURL = verifyURL(url);
		if (verifiedURL == null) {
			logger.warning("Invalid URL");
			return;
		}
		logger.info("URL verified");

		urlInfo.fileName  = verifiedURL.substring(verifiedURL.lastIndexOf('/') + 1);
		urlInfo.port = getPort(verifiedURL);
		urlInfo.filePath = getPath(verifiedURL);
		urlInfo.host = getHost(url);
		this.start();
	}


	// Method to verify URL. Returns the valid URL, null if invalid.
	private static String verifyURL(String url) {
		// Make sure URL starts with http://
		if (!url.startsWith("http://")) {
			return null;
		}

		// Make sure URL specifies a file.
		if (url.lastIndexOf('.') == -1) {
			return null;
		}

		return url;
	}

	// Method to find port number
	private static int getPort(String url) {
		Pattern regex = Pattern.compile(":\\d+");
		Matcher match = regex.matcher(url);

		while (match.find()) {
			return Integer.parseInt(match.group().substring(1));
		}

		// Return default port if no port number is found
		return 80;
	}

	// Method to find Host
	private static String getHost(String url) {
		Pattern regex = Pattern.compile("http://[\\w\\d.]+");
		Matcher match = regex.matcher(url);

		while (match.find()) {
			return match.group().substring(match.group().lastIndexOf('/') + 1);
		}
		return "";
	}

	// Method to find path
	public static String getPath(String url) {
		Pattern regex = Pattern.compile("http://[\\w\\d.]+");
		Matcher match = regex.matcher(url);

		while (match.find()) {
			return url.substring(match.group().length());
		}
		return "";
	}

	// Method used for establishing connection to server
	void connectToServer() throws IOException {
		socket = new Socket(urlInfo.host, urlInfo.port);
		inFromServer =
			new BufferedReader(new InputStreamReader(socket.getInputStream()));
		outToServer = new DataOutputStream(socket.getOutputStream());
	}

	@Override
	public void run() {
		boolean isHeader = true;
		String header;
		String status = null;
		LinkedHashMap<String, String> headers = new LinkedHashMap<String, String>();
		headers.put("GET", urlInfo.filePath + " HTTP/1.1");
		headers.put("Host:", urlInfo.host);

		try {
			connectToServer();
		} catch (IOException e) {
			logger.warning(e.getMessage());
			return;
		}

		try {
			// Sending "GET" request in order to extract information from the Response headers.
			for (Map.Entry h : headers.entrySet()) {
				outToServer.writeBytes(h.getKey() + " " + h.getValue() + NEW_LINE);
  		}
			outToServer.writeBytes(NEW_LINE);

			while((header = inFromServer.readLine()) != null && isHeader) {
				// Extract status code
				if (header.startsWith("HTTP/1.1")) {
					int startByte = header.indexOf(' ') + 1;
					int endByte = header.indexOf(' ', startByte);
					statusCode = Integer.parseInt(header.substring(startByte, endByte));
					status = header.substring(startByte);
				}
				// Extract content length
				if (header.startsWith("Content-Length:")) {
					contentLength =
						Integer.parseInt(header.substring(header.indexOf(' ') + 1));
				}

				if (header.equals("")) {
					isHeader = false;
				}
			}
			inFromServer.close();
		} catch (IOException e) {
			logger.warning(e.getMessage());
			return;
		}

		// If download is possible
		if (statusCode <= 226 && statusCode >= 200) {
			logger.info("Starting Download");
			downloadThreads = new DownloadThread[threadCount];
			int partLength = (contentLength / threadCount);
			int remain = (contentLength % threadCount);
			int startByte = 0;
			int endByte = partLength - 1;

			// Starting multiple worker threads to download parts of the file simultaneously.
			for (int ii = 0; ii < threadCount; ii++) {
				try {
					downloadThreads[ii] =	new DownloadThread(
						startByte,
						endByte + ((ii < threadCount - 1) ? 0 : remain),
						urlInfo
						);
				} catch(java.io.FileNotFoundException e) {
					logger.warning("Error occured. " + e.getMessage());
					return;
				}

				startByte = endByte + 1;
				endByte += partLength;
			}
			logger.info("Downloading...");

			for (int ii = 0; ii < threadCount; ii++) {
				try {
					downloadThreads[ii].join(); // Wait for all the threads to finish execution.
				} catch (InterruptedException e) {
					logger.warning(e.getMessage());
				}
			}
			logger.info("Download complete");
		}

		// If download is not possible
		else {
			logger.warning("Error occured. " + status);
		}
	}
}
