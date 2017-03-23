/** Java code to implement a Multithreaded Download Manager
  * It divides the incoming file into n parts and each part is downloaded by an individual thread
  * The value of n is scanned as CommandLine Argument (MAX 20)
  */
import java.util.*;
import java.io.*;
import java.net.*;

// Class containing the main method
class Assignment2_2 {
  // main method
  public static void main(String args[]) {
    Scanner scanner = new Scanner(System.in);
    if (args.length == 0) {
      System.out.println("Please enter the number of parts of the file as CommandLine Argument (MAX 20)");
    }
    else {
      try {
        int threadCount = Integer.parseInt(args[0]);
        if (threadCount <= 0 || threadCount > 20) {
          throw new NumberFormatException();
        }
        System.out.println("Enter the URL");
        String url = scanner.nextLine();
        DownloadManager manager = new DownloadManager(url, threadCount);
      }
        catch(NumberFormatException e) {
        System.out.println("Number of parts should be a positive Integer and less than 21");
        }
    }
  }
}

// Class which manages the Download process
class DownloadManager {
  private String downloadUrl;
  private String fileName;
  private String fileExtension;
  private URL nonStringUrl;
  private HttpURLConnection connection;
  private int fileSize;
  private int remainingByte;
  private RandomAccessFile outputFile;
  private boolean downloadPossible = true;
  private int threadCount;
  // Constructor
  public DownloadManager(String downloadUrl, int threadCount) {
    this.downloadUrl = downloadUrl;
    this.threadCount = threadCount;
    initiateDownload();
  }

  private void initiateDownload() {
    fileName = downloadUrl.substring(downloadUrl.lastIndexOf('/') + 1, downloadUrl.length());
    fileExtension = downloadUrl.substring(downloadUrl.lastIndexOf('.') + 1, downloadUrl.length());

    try {
      nonStringUrl = new URL(downloadUrl);
      connection = (HttpURLConnection) nonStringUrl.openConnection();
      System.out.println("Preparing to download...");
      fileSize = connection.getContentLength();
      // Printing details of the file to be downloaded
      System.out.println("File size - " + (double) fileSize/1000.0 + "KB");
      System.out.println("File Name - " + fileName);
      System.out.println("File Extension - " + fileExtension);
      fileSize = fileSize / threadCount;
      System.out.println("Partition size - " + (double) fileSize/1000.0 + "KB");
      remainingByte = fileSize % threadCount;
      outputFile = new RandomAccessFile(fileName, "rw");
    } catch(MalformedURLException e) {
        System.out.println("Invalid URL");
        downloadPossible = false;
    } catch(IOException e) {
        System.out.println("IO failed");
        downloadPossible = false;
    }
    int first = 0;
    int last = fileSize - 1;
    if(downloadPossible) {
      System.out.println("Downloading...");
      Downloader downloadParts[] = new Downloader[threadCount];
      // Creating and starting threads to download different parts of the file
      for (int i = 0; i < threadCount; i++) {
        if (i < threadCount) {
          downloadParts[i] = new Downloader(nonStringUrl, first, last, (i+1), outputFile);
          downloadParts[i].start();
          try{
            downloadParts[i].join();
          } catch(InterruptedException e) {}
        }
        else {
          downloadParts[i] = new Downloader(nonStringUrl, first, last + remainingByte, (i+1), outputFile);
          downloadParts[i].start();
          try{
            downloadParts[i].join();
          } catch(InterruptedException e) {}
        }
        first = last + 1;
        last += fileSize;
        }
      System.out.println("Download Complete");
    }
    else
      System.out.println("Download Failed");
  }
}

// Class responsible for downloading file
class Downloader extends Thread {
  private URL downloadURL;
  private int startByte;
  private int endByte;
  private int threadNum;
  private RandomAccessFile outputFile;
  private InputStream stream;

  // Constructor
  public Downloader(URL downloadURL, int startByte, int endByte, int threadNum, RandomAccessFile outputFile) {
    this.downloadURL = downloadURL;
    this.startByte = startByte;
    this.endByte = endByte;
    this.threadNum = threadNum;
    this.outputFile = outputFile;
  }

  @Override
  public void run() {
    try {
      HttpURLConnection httpURLConnection = (HttpURLConnection) downloadURL.openConnection();
      httpURLConnection.setRequestProperty("Range", "bytes = " + startByte + " - " + endByte);
      httpURLConnection.connect();
      outputFile.seek(startByte);
      stream = httpURLConnection.getInputStream();
      while (true) {
        int nextByte = stream.read();
        if (nextByte == -1)
          break;
          outputFile.write(nextByte);
        }
    } catch(IOException e) {}
  }

}
