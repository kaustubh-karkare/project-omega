package httpserver;

import java.io.*;
import java.net.*;
import java.util.*;
import java.util.logging.*;

// A Webserver waits for clients to connect, then starts a separate thread to handle the request.
public class HttpServer extends Thread {
  private final static Logger logger = Logger.getLogger(HttpServer.class.getName());
  private static FileHandler fileHandler = null;
  static ServerSocket serverSocket;
  static String inputPort;
  static int port;

  public HttpServer(String inputPort) {
    HttpServer.inputPort = inputPort;
  }

  // Method to create log file
  public static void initLog() throws SecurityException, IOException {
    fileHandler = new FileHandler("Status.log", false);
    Logger logger = Logger.getLogger("");
    fileHandler.setFormatter(new SimpleFormatter());
    logger.addHandler(fileHandler);
    logger.setLevel(Level.FINE);
  }
  // The run() method of HttpServer
  @Override
  public void run() {
    try {
      initLog();
      try {
        port = Integer.parseInt(inputPort);
        if (port <= 0)
          throw new NegativeNumberException();
        serverSocket = new ServerSocket(port); // Start,listen on given port
        while (true) {
          try {
            logger.info("TCPServer Waiting for client on port " + port);
            Socket socket = serverSocket.accept(); // Wait for a client to connect
            new ClientHandler(socket); // A separate thread to handle each client
          } catch (IOException e) {
            e.printStackTrace();
          }
        }
      } catch (NumberFormatException | NegativeNumberException e) {
        logger.warning("Port number should be a positive integer");
      } catch (ArrayIndexOutOfBoundsException e) {
        logger.warning("Port number must be entered as command line argument");
      } catch (IOException e) {
        System.out.println("Unable to start server on port " + port);
      }
    } catch (SecurityException | IOException e) {
      System.out.println("Unable to create log file. Can't start server");
    }
  }
}

// A ClientHandler reads an HTTP request and responds
class ClientHandler extends Thread {
  private static final Logger logger = Logger.getLogger(ClientHandler.class.getName());
  static final String HTML_START =
    "<html>" +
    "<title>HTTP Server in java</title>" +
    "<body>";
  static final String HTML_END = "</body>" + "</html>";
  private Socket connectedClient = null;
  private BufferedReader inFromClient = null;
  private DataOutputStream outToClient = null;

  // Constructor where thread startsWith
  public ClientHandler(Socket connectedClient) {
    this.connectedClient = connectedClient;
    start();
  }

  @Override
  public void run() {

    try {
      logger.info(
        "The Client " +
        connectedClient.getInetAddress() +
        ":" +
        connectedClient.getPort() +
        " is connected");
      inFromClient = new BufferedReader(new InputStreamReader(connectedClient.getInputStream()));
      outToClient = new DataOutputStream(connectedClient.getOutputStream());
      String headerLine = inFromClient.readLine();
      String httpMethod = headerLine.substring(0,3);
      String httpQueryString = headerLine.substring(
        4, headerLine.indexOf(" ", headerLine.indexOf(" ") + 1));

      if (httpMethod.equals("GET")) {
        String requestPath = httpQueryString.replaceFirst("/", "");
        // if request is for a directory
        if (requestPath.endsWith("/") | httpQueryString.equals("/")) {
          try {
            sendDirectoryInformation(requestPath);
          } catch (Exception e) {
            sendResponse(404, "", false);
          }
        }

        // if request is for a file
        else {
          if (new File(requestPath).isFile()) {
            sendResponse(200, requestPath, true);
          }
          else {
            sendResponse(404, "", false);
          }
        }
      }
      sendResponse(404, "", false);
    } catch (IOException e) {
      logger.info(
        "The Client " +
        connectedClient.getInetAddress() +
        ":" +
        connectedClient.getPort() +
        " is disconnected");
    }
  }

  public void sendDirectoryInformation(String requestPath) throws Exception  {
    String indexFile = requestPath + "index.html";
    // if index.html exists
    if (new File(indexFile).isFile()) {
      sendResponse(200, indexFile, true);
    }
    // if index.html does not exists, we send the list of files and folders in that directory
    else {
      File folder;
      String inetAddress = HttpServer.serverSocket.getInetAddress().toString();
      // If homepage is requested
      if (requestPath.equals("")) {
        requestPath = ".";
        folder = new File(requestPath);
      }
      else
        folder = new File(requestPath.substring(0, requestPath.lastIndexOf('/')));
      File[] listOfFiles = folder.listFiles();
      StringBuffer response = new StringBuffer();
      response.append("<b>List of files and folders</b> <BR>");
      response.append("<ul>");
      for (int i = 0; i < listOfFiles.length; i++) {
        if (listOfFiles[i].isFile()) {
          response.append("<li>File - " +
            "<a href=" +
            inetAddress.substring(0, inetAddress.indexOf("0.0.0.0")) +
            "/" +
            requestPath +
            "/" +
            listOfFiles[i].getName() +
            ">" +
            listOfFiles[i].getName() +
            "</a></li><BR>");
        }
        else if (listOfFiles[i].isDirectory()) {
          response.append("<li>Folder - " +
            "<a href=" +
            inetAddress.substring(0, inetAddress.indexOf("0.0.0.0")) +
            "/" +
            requestPath +
            "/" +
            listOfFiles[i].getName() +
            "/>" +
            listOfFiles[i].getName() +
            "</a></li><BR>");
        }
      }
      response.append("</ul>");
      sendResponse(200, response.toString(), false);
    }
  }

  public void sendResponse(int statusCode, String responseString, boolean isFile) throws IOException {
    String statusLine = null;
    String serverdetails = "Server: Java HTTPServer";
    String contentLengthLine = null;
    String requestPath = null;
    String contentType = null;
    String contentTypeLine = "Content-Type: text/html" + "\r\n";
    FileInputStream fileInputStream = null;

    if (statusCode == 200)
      statusLine = "HTTP/1.1 200 OK" + "\r\n";
    else
      statusLine = "HTTP/1.1 404 Not Found" + "\r\n";

    if (isFile) {
      requestPath = responseString;
      contentType = responseString.substring(responseString.lastIndexOf('.'), responseString.length());
      fileInputStream = new FileInputStream(requestPath);
      contentLengthLine = "Content-Length: " + Integer.toString(fileInputStream.available()) + "\r\n";
      if (!requestPath.endsWith(".htm") && !requestPath.endsWith(".html"))
      contentTypeLine = "Content-Type: " + contentType + "\r\n";
    }
    else {
      responseString = ClientHandler.HTML_START + responseString + ClientHandler.HTML_END;
      contentLengthLine = "Content-Length: " + responseString.length() + "\r\n";
    }

    outToClient.writeBytes(statusLine);
    outToClient.writeBytes(serverdetails);
    outToClient.writeBytes(contentTypeLine);
    outToClient.writeBytes(contentLengthLine);
    outToClient.writeBytes("Connection: close\r\n");
    outToClient.writeBytes("\r\n");

    if (isFile)
     sendFile(fileInputStream, outToClient);
    else
      outToClient.writeBytes(responseString);

    outToClient.close();
  }

  public void sendFile(FileInputStream fileInputStream, DataOutputStream out) throws IOException {
    byte[] buffer = new byte[1024] ;
    int bytesRead;

    while ((bytesRead = fileInputStream.read(buffer)) != -1) {
      out.write(buffer, 0, bytesRead);
    }
    fileInputStream.close();
  }

}

// User defined exception class
class NegativeNumberException extends Exception {
  public NegativeNumberException() {
    super("Port should be a positive integer");
  }
}
