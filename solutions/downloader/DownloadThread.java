// Worker thread responsible for downloading a part of the file.
package downloader;

import java.io.BufferedInputStream;
import java.io.BufferedReader;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.RandomAccessFile;
import java.net.Socket;
import java.net.URL;
import java.net.UnknownHostException;
import java.util.logging.Logger;
import java.util.LinkedHashMap;
import java.util.Map;

public class DownloadThread extends Thread {
	private final static Logger logger =
		Logger.getLogger(FileDownloader.class.getName());
	private final static String NEW_LINE = "\r\n";
	protected static final int BUFFER_SIZE = 4096;
	private int startByte;
	private int endByte;
	private Socket socket;
	private URLInfo urlInfo;
	private BufferedInputStream inFromServer = null;
	private DataOutputStream outToServer = null;
	private RandomAccessFile outputFile;

	public DownloadThread(int startByte, int endByte, URLInfo urlInfo)
		throws FileNotFoundException {
		this.urlInfo = urlInfo;
		this.startByte = startByte;
		this.endByte = endByte;
		outputFile = new RandomAccessFile(urlInfo.fileName, "rw");

		this.start();
	}

	private void connectToServer() throws IOException {
		socket = new Socket(urlInfo.host, urlInfo.port);
		inFromServer = new BufferedInputStream(socket.getInputStream());
		outToServer = new DataOutputStream(socket.getOutputStream());
	}

	@Override
	public void run() {
		byte data[] = new byte[BUFFER_SIZE];
		int numRead;
		int offset = 0;
		boolean isHeader = true;
		LinkedHashMap<String, String> headers = new LinkedHashMap<String, String>();
		headers.put("GET", urlInfo.filePath + " HTTP/1.1");
		headers.put("Host:", urlInfo.host);
		headers.put("Range:", "bytes=" + startByte + "-" + endByte);

		try {
			connectToServer();
			outputFile.seek(startByte);
		} catch (IOException e) {
			e.printStackTrace();
		}

		try {
			// Sending "GET" request to the server for specific range
			for (Map.Entry h : headers.entrySet()) {
				outToServer.writeBytes(h.getKey() + " " + h.getValue() + NEW_LINE);
  		}
			outToServer.writeBytes(NEW_LINE);
			outToServer.flush();
			int total = 0;
			
			while ((numRead = inFromServer.read(data, 0, BUFFER_SIZE)) != -1) {
				// Downloading the file by filtering the response headers.
				offset = 0;
				total += numRead;
				if (isHeader) {
					String string = new String(data, 0, numRead);
					int indexOfEOH = string.indexOf(NEW_LINE + NEW_LINE);

					if (indexOfEOH != -1) {
						numRead = numRead - indexOfEOH - 4;
						offset = indexOfEOH + 4;
						isHeader = false;
					}

					else {
						numRead = 0;
					}
				}

				outputFile.write(data, offset, numRead);
			}

			logger.info(this.getName() + " Executed");
		} catch (IOException e) {
			logger.warning(e.getMessage());
		}
		finally {
      if (outputFile != null) {
        try {
          outputFile.close();
        } catch(IOException e) {}
      }
      if (inFromServer != null) {
        try {
          inFromServer.close();
        } catch(IOException e) {}
      }
		}
	}
}
