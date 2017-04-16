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

public class DownloadThread extends Thread {
	private final static Logger logger = Logger.getLogger(FileDownloader.class.getName());	
	private final static String newLine = "\r\n";
	private static final int BUFFER_SIZE = 4096;
	private int startByte;
	private int endByte;
	private Socket socket;
	private BufferedInputStream inFromServer = null;
	private DataOutputStream outToServer = null;
	private RandomAccessFile outputFile;	
	
	public DownloadThread(int startByte, int endByte) {		
		this.startByte = startByte;
		this.endByte = endByte;
		
		try {
			outputFile = new RandomAccessFile(FileDownloader.fileName, "rw");
		} catch (FileNotFoundException e) {
			logger.warning(e.getMessage());
		}
		
		this.start();
	}
	
	@Override 
	public void run() {
		byte data[] = new byte[BUFFER_SIZE];
		int numRead;
		int offset = 0;	
		boolean isHeader = true;
		
		try {
			socket = new Socket(FileDownloader.host, FileDownloader.port);
			inFromServer = new BufferedInputStream(socket.getInputStream());
			outToServer = new DataOutputStream(socket.getOutputStream());
			outputFile.seek(startByte);				
		} catch (IOException e) {			
			e.printStackTrace();
		}	
		
		try {
			// Sending "GET" request to the server for specific range
			outToServer.writeBytes("GET " + FileDownloader.verifiedURL.getPath() + " HTTP/1.1" + newLine);		
			outToServer.writeBytes("Host: " + FileDownloader.host + newLine);
			outToServer.writeBytes("Range: bytes=" + startByte + "-" + endByte + newLine + newLine);
			outToServer.flush();
			
			while ((numRead = inFromServer.read(data, 0, BUFFER_SIZE)) != -1) {
				// Downloading the file by filtering the response headers.
				offset = 0;
				
				if (isHeader) {
					String string = new String(data, 0, numRead);
					int indexOfEOH = string.indexOf(newLine + newLine);
					
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
	}
}
