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
import java.net.URL;
import java.util.logging.Logger;

public class FileDownloader extends Thread {	
	private final static Logger logger = Logger.getLogger(FileDownloader.class.getName());
	private final static String newLine = "\r\n";
	private Socket socket;
	private int contentLength;
	private int statusCode;		
	private int threadCount;	
	private DownloadThread downloadThreads[];	
	
	protected static URL verifiedURL;
	protected static String fileName;
	protected static int port;
	protected static String host;	
	
	public FileDownloader(String url, int threadCount) {		
		this.threadCount = threadCount;
		
		verifiedURL = verifyURL(url);		
		if (verifiedURL == null) {
			logger.warning("Invalid URL");
			return;
		}		
		logger.info("URL verified");
		
		String fileURL = verifiedURL.getFile();
		fileName = fileURL.substring(fileURL.lastIndexOf('/') + 1);
		
		port = verifiedURL.getPort();		
		if (port == -1) {
			port = 80;
		}
		
		host = verifiedURL.getHost();		
		this.start();
	}
	
	// Method to verify URL. Returns the valid URL, null if invalid.
	private URL verifyURL(String url) {
		// Only allow HTTP URLs.
        if (!url.toLowerCase().startsWith("http://"))
            return null;
        
        // Verify format of URL.
        URL verifiedUrl = null;
        try {
            verifiedUrl = new URL(url);
        } catch (MalformedURLException e) {
            return null;
        }
        
        // Make sure URL specifies a file.
        if (verifiedUrl.getFile().length() < 2)
            return null;
        
        return verifiedUrl;
	}
	
	@Override
	public void run() {		
		BufferedReader inFromServer = null;
		DataOutputStream outToServer = null;
		boolean isHeader = true;
		String header;
		String status = null;
		
		try {
			socket = new Socket(host, port);		
			inFromServer = new BufferedReader(new InputStreamReader(socket.getInputStream()));
		    outToServer = new DataOutputStream(socket.getOutputStream());
		} catch (IOException e) {
			logger.warning(e.getMessage());	
			return;
		}	
		
		try {
			// Sending "GET" request in order to extract information from the Response headers.
			outToServer.writeBytes("GET " + verifiedURL.getPath() + " HTTP/1.1" + newLine);		
			outToServer.writeBytes("Host: " + host + newLine + newLine);				
			
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
					contentLength = Integer.parseInt(header.substring(header.indexOf(' ') + 1));
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
				if (ii < threadCount - 1) {
					downloadThreads[ii] = new DownloadThread(startByte, endByte);						
				}	
				
				else {
					downloadThreads[ii] = new DownloadThread(startByte, endByte + remain);
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
