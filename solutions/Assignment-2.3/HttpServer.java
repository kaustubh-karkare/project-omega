/**
 * JAVA code to implement a webserver that can handle basic GET requests.
 * The HTTPServer waits for requests in the main thread and handles the requests
 * in a separate ClientHandler thread.
 */
import java.io.*;
import java.net.*;
import java.util.*;
import java.util.logging.*;

// A Webserver waits for clients to connect, then starts a separate thread to handle the request.
public class HttpServer {
  private final static Logger logger = Logger.getLogger(HttpServer.class.getName());
  private static FileHandler fileHandler = null;
  private static ServerSocket serverSocket;
  private static int port;
  // Method to create log file
  public static void initLog(){
    try {
      fileHandler = new FileHandler("Status.log", false);
    }
    catch (SecurityException | IOException e) {
      e.printStackTrace();
    }
    Logger logger = Logger.getLogger("");
    fileHandler.setFormatter(new SimpleFormatter());
    logger.addHandler(fileHandler);
    logger.setLevel(Level.FINE);
  }

  public static void main(String args[]) throws IOException {
    initLog();
    try {
      port = Integer.parseInt(args[0]);
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
    } catch (NumberFormatException e) {
        logger.warning("Port number should be a positive integer");
    } catch (ArrayIndexOutOfBoundsException e) {
        logger.warning("Port number must be entered as command line argument");
    }

  }
}

// A ClientHandler reads an HTTP request and responds
class ClientHandler extends Thread {
  private static final Logger logger = Logger.getLogger(ClientHandler.class.getName());
  static final String HTML_START = "<html>" + "<title>HTTP Server in java</title>" +
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
      logger.info("The Client " + connectedClient.getInetAddress() +
        ":" + connectedClient.getPort() + " is connected");
      inFromClient = new BufferedReader(new InputStreamReader (connectedClient.getInputStream()));
      outToClient = new DataOutputStream(connectedClient.getOutputStream());
      String requestString = inFromClient.readLine();
      String headerLine = requestString;
      StringTokenizer tokenizer = new StringTokenizer(headerLine);
      String httpMethod = tokenizer.nextToken();
      String httpQueryString = tokenizer.nextToken();
      StringBuffer responseBuffer = new StringBuffer();
      logger.info("The HTTP request string is...<BR>");
      responseBuffer.append("<b> This is the HTTP Server Home Page.... </b><BR>");
      responseBuffer.append("Created by DJ<BR>");
      while (inFromClient.ready()) {
        // Read the HTTP Complete Query
        logger.info(requestString);
        requestString = inFromClient.readLine();
      }
      if (httpMethod.equals("GET")) {
        if (httpQueryString.equals("/")) {
          // The default home Page
          sendResponse(200, responseBuffer.toString(), false);
        }
        else {
          String fileName = httpQueryString.replaceFirst("/", "");

          // if request is for a directory
          if (fileName.endsWith("/")) {
            String indexFile = fileName + "index.html";

            // if index.html exists
            if (new File(indexFile).isFile()) {
              sendResponse(200, indexFile, true);
            }
            // if index.html does not exists, we send the list of files and folders in that directory
            else {
              try {
                File folder = new File(fileName.substring(0, fileName.lastIndexOf('/')));
                File[] listOfFiles = folder.listFiles();
                StringBuffer response = new StringBuffer();
                response.append("<b>List of files and folders</b> <BR>");
                for (int i = 0; i < listOfFiles.length; i++) {
                  if (listOfFiles[i].isFile()) {
                    response.append("File - " + listOfFiles[i].getName() + "<BR>");
                  }
                  else if (listOfFiles[i].isDirectory()) {
                    response.append("Folder -  " + listOfFiles[i].getName() + "<BR>");
                  }
                }
                sendResponse(200, response.toString(), false);
              } catch (NullPointerException e) {
                sendResponse(404, "<b>" +
                  "Error 404: The Requested resource not found ....</b>", false);
              }
            }
          }

          // if request is for a file
          else {
            if (new File(fileName).isFile()) {
              sendResponse(200, fileName, true);
            }
            else {
              sendResponse(404, "<b>" +
                "Error 404: The Requested resource not found ....</b>", false);
            }
          }
        }
      }
      sendResponse(404, "<b>" +
        "Error 404: The Requested resource not found ....</b>", false);
    } catch (IOException e) {
        e.printStackTrace();
    }
  }

  public void sendResponse(int statusCode, String responseString, boolean isFile) throws IOException {
    String statusLine = null;
    String serverdetails = "Server: Java HTTPServer";
    String contentLengthLine = null;
    String fileName = null;
    String contentTypeLine = "Content-Type: text/html" + "\r\n";
    FileInputStream fileInputStream = null;

    if (statusCode == 200)
      statusLine = "HTTP/1.1 200 OK" + "\r\n";
    else
      statusLine = "HTTP/1.1 404 Not Found" + "\r\n";

    if (isFile) {
      fileName = responseString;
      fileInputStream = new FileInputStream(fileName);
      contentLengthLine = "Content-Length: " + Integer.toString(fileInputStream.available()) + "\r\n";
      if (!fileName.endsWith(".htm") && !fileName.endsWith(".html"))
      contentTypeLine = "Content-Type: \r\n";
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

    while ((bytesRead = fileInputStream.read(buffer)) != -1 ) {
      out.write(buffer, 0, bytesRead);
    }
    fileInputStream.close();
  }

}
