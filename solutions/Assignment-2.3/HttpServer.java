package httpserver;

import java.io.*;
import java.net.*;
import java.util.*;
import java.util.logging.*;

// A Webserver waits for clients to connect, then starts a separate thread to handle the request.
public class HttpServer extends Thread {
  private static final LogManager logManager = LogManager.getLogManager();
  private final static Logger logger = Logger.getLogger(HttpServer.class.getName());  
  static ServerSocket serverSocket;
  static String inputPort;
  static int port;

  public HttpServer(String inputPort) {
    HttpServer.inputPort = inputPort;
    try {
      initLog();
    } catch (SecurityException | IOException e) {
      logger.severe("Some error occured in loading configuration. Logging through console only");
    }
  }

  // Method to create log file
  public static void initLog() throws SecurityException, IOException {
    Logger logger = Logger.getLogger("");
    // Reading Configuration file which contains predefined instructions regarding logging
    logManager.readConfiguration(new FileInputStream("./server.properties"));
  }
  // The run() method of HttpServer
  @Override
  public void run() {

    try {
      port = Integer.parseInt(inputPort);
      if (port < 0) {
        throw new NegativeNumberException();
      }
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
      logger.warning("Unable to start server on port " + port);
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
  private Socket socket = null;
  private BufferedReader inFromClient = null;
  private DataOutputStream outToClient = null;
  private enum FileSendingDecision {
    SEND_FILE,
    DONT_SEND_FILE
  }

  // Constructor where thread startsWith
  public ClientHandler(Socket socket) throws IOException {
    this.socket = socket;
    inFromClient = new BufferedReader(new InputStreamReader(socket.getInputStream()));
    outToClient = new DataOutputStream(socket.getOutputStream());
    start();
  }

  @Override
  public void run() {

    try {
      logger.info(
        "The Client " +
        socket.getInetAddress() +
        ":" +
        socket.getPort() +
        " is connected"
      );
      String headerLine = inFromClient.readLine();
      String[] tokens = headerLine.split("\\s");
      String httpMethod = tokens[0];
      String httpQueryString = tokens[1].substring(1);

      if (httpMethod.equals("GET")) {
        String requestPath = httpQueryString;

        // If requestPath ends with a '/' or is empty, it is a request for a directory
        if (requestPath.endsWith("/") | httpQueryString.isEmpty()) {
          try {
            sendDirectoryInformation(requestPath);
          } catch (Exception e) {
            sendResponse(500, "", FileSendingDecision.DONT_SEND_FILE);
          }
        }

        // If request is for a file
        else {
          if (new File(requestPath).isFile()) {
            sendResponse(200, requestPath, FileSendingDecision.SEND_FILE);
          }
        }
      }
      sendResponse(404, "", FileSendingDecision.DONT_SEND_FILE);
    } catch (IOException e) {
      logger.info(
        "The Client " +
        socket.getInetAddress() +
        ":" +
        socket.getPort() +
        " is disconnected"
      );
    }
  }

  public void sendDirectoryInformation(String requestPath) throws Exception  {
    String indexFile = requestPath + "index.html";
    // if index.html exists
    if (new File(indexFile).isFile()) {
      sendResponse(200, indexFile, FileSendingDecision.SEND_FILE);
      return;
    }
    // if index.html does not exists, we send the list of files and folders in that directory
    File folder;
    // If homepage is requested
    if (requestPath.equals("")) {
      folder = new File(".");
    }
    else {
      folder = new File(requestPath.substring(0, requestPath.lastIndexOf('/')));
    }
    File[] listOfFiles = folder.listFiles();
    StringBuffer response = new StringBuffer();
    response.append("<b>List of files and folders</b> <br>");
    response.append("<ul>");
    for (int ii = 0; ii < listOfFiles.length; ii++) {
      if (listOfFiles[ii].isFile()) {
        response.append("<li>File - " +
          "<a href=" +
          "/" +
          requestPath +
          listOfFiles[ii].getName() +
          ">" +
          listOfFiles[ii].getName() +
          "</a></li>");
      }
      else if (listOfFiles[ii].isDirectory()) {
        response.append("<li>Folder - " +
          "<a href=" +
          "/" +
          requestPath +
          listOfFiles[ii].getName() +
          "/>" +
          listOfFiles[ii].getName() +
          "</a></li>"
        );
      }
    }
    response.append("</ul>");
    sendResponse(200, response.toString(), FileSendingDecision.DONT_SEND_FILE);
  }

  public void sendResponse(int statusCode, String responseString, FileSendingDecision decision)
    throws IOException {
    final String newLine = "\r\n";
    HashMap<String, String> headers = new HashMap<String, String>();
    headers.put("statusLine", null);
    headers.put("serverdetails", "Server: Java HTTPServer");
    headers.put("contentLengthLine", null);
    headers.put("requestPath", null);
    headers.put("contentTypeLine", "Content-Type: text/html" + newLine);
    headers.put("closeConnection", "Connection: close" + newLine);

    FileInputStream fileInputStream = null;

    if (statusCode == 200) {
      headers.put("statusLine", "HTTP/1.1 200 OK" + newLine);
    }
    else if (statusCode == 404) {
      headers.put("statusLine", "HTTP/1.1 404 Not Found" + newLine);
    }
    else if (statusCode == 500) {
      headers.put("statusLine", "HTTP/1.1 500 Internal Server Error" + newLine);
    }

    if (decision == FileSendingDecision.SEND_FILE) {
      headers.put("requestPath", responseString);
      String contentType = responseString.substring(
        responseString.lastIndexOf('.'),
        responseString.length()
      );
      fileInputStream = new FileInputStream(headers.get("requestPath"));
      headers.put(
        "contentLengthLine", "Content-Length: " +
        Integer.toString(fileInputStream.available()) +
        newLine
      );
      if (!headers.get("requestPath").endsWith(".htm") && !headers.get("requestPath").endsWith(".html"))
      headers.put("contentTypeLine", "Content-Type: " + contentType + newLine);
    }
    else {
      responseString = ClientHandler.HTML_START + responseString + ClientHandler.HTML_END;
      headers.put("contentLengthLine", "Content-Length: " + responseString.length() + newLine);
    }

    outToClient.writeBytes(headers.get("statusLine"));
    outToClient.writeBytes(headers.get("serverdetails"));
    outToClient.writeBytes(headers.get("contentTypeLine"));
    outToClient.writeBytes(headers.get("contentLengthLine"));
    outToClient.writeBytes(headers.get("closeConnection"));
    outToClient.writeBytes(newLine);

    if (decision == FileSendingDecision.SEND_FILE) {
      sendFile(fileInputStream, outToClient);
    }
    else {
      outToClient.writeBytes(responseString);
    }

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
