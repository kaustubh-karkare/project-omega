package httpserver;

import java.io.*;
import java.net.*;
import java.util.*;
import java.util.logging.*;

// A ClientHandler reads an HTTP request and responds
public class ClientHandler extends Thread {
  private static final Logger logger = Logger.getLogger(ClientHandler.class.getName());
  static final String HTML_START =
    "<html>" +
    "<title>HTTP Server in java</title>" +
    "<body>";
  static final String HTML_END = "</body>" + "</html>";
  private static HashMap<Integer, String> statusCodes;
  // Static block to initialize the HashMap.
  static {
    statusCodes = new HashMap<Integer, String>();
    statusCodes.put(200, "OK");
    statusCodes.put(404, "Not Found");
    statusCodes.put(500, "Internal Server Error");
    statusCodes.put(415, "Unsupported Media Type");
  }

  private Socket socket = null;
  private BufferedReader inFromClient = null;
  private DataOutputStream outToClient = null;
  private LinkedHashMap<String, String> headers;

  private enum FileSendingDecision {
    SEND_FILE,
    DONT_SEND_FILE
  }

  // Constructor where thread starts
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
        " is connected."
      );
      String headerLine = inFromClient.readLine();
      String[] tokens = headerLine.split("\\s");
      String httpMethod = tokens[0];
      String httpQueryString = tokens[1].substring(1);

      if (httpMethod.equals("GET")) {
        String requestPath = httpQueryString;
        requestPath = URLDecoder.decode(requestPath, "UTF-8");

        // If request is for a directory
        if (new File(requestPath).isDirectory() | httpQueryString.isEmpty()) {
          logger.info("Directory requested. Looking for index.html...");
          String indexFile = requestPath + "index.html";

          if (new File(indexFile).isFile()) {
            logger.info("index.html found. Sending index.html...");
            sendResponse(200, indexFile, FileSendingDecision.SEND_FILE);
            return;
          }
          logger.info(
            "index.html not found." +
            " Generating list of files and folders in the requested directory."
          );
          try {
            sendDirectoryInformation(requestPath);
          } catch (Exception e) {
            logger.warning("Internal Server Error occured - " + e.getMessage());
            sendResponse(500, "", FileSendingDecision.DONT_SEND_FILE);
          }
        }

        // If request is for a file
        else if (new File(requestPath).isFile()) {
          logger.info("File requested. Preparing to send file - " + requestPath);
          sendResponse(200, requestPath, FileSendingDecision.SEND_FILE);
        }

        // If request is neither for a folder or file, then it means requested resource is not found
        else {
          sendResponse(404, "", FileSendingDecision.DONT_SEND_FILE);
          logger.info(requestPath + " - Requested resource not found.");
        }
      }

      else {
        sendResponse(405, "", FileSendingDecision.DONT_SEND_FILE);
        logger.info(httpMethod + " requested. Denied.");
      }

    } catch (IOException e) {
      logger.info(
        "The Client " +
        socket.getInetAddress() +
        ":" +
        socket.getPort() +
        " is disconnected."
      );
    }
  }

  public void sendDirectoryInformation(String requestPath) throws Exception {
    File folder;
    // If homepage is requested
    if (requestPath.equals("")) {
      folder = new File(".");
    }
    else {
      folder = new File(requestPath);
    }
    File[] listOfFiles = folder.listFiles();
    StringBuffer response = new StringBuffer();
    response.append("<b>List of files and folders</b>");
    response.append("<ul>");
    for (int ii = 0; ii < listOfFiles.length; ii++) {
      if (listOfFiles[ii].isFile()) {
        String path = URLEncoder.encode(listOfFiles[ii].toString(), "UTF-8");
        String fileName = listOfFiles[ii].getName();
        response.append(
          "<li>File - " +
          "<a href='/" +
          path +
          "'>" +
          fileName +
          "</a></li>"
        );
      }
      else if (listOfFiles[ii].isDirectory()) {
        String path = URLEncoder.encode(listOfFiles[ii].toString(), "UTF-8");
        String folderName = listOfFiles[ii].getName();
        response.append(
          "<li>Folder - " +
          "<a href='/" +
          path +
          "/'>" +
          folderName +
          "</a></li>"
        );
      }
    }
    response.append("</ul>");
    String responseString = response.toString();
    responseString = ClientHandler.HTML_START + responseString + ClientHandler.HTML_END;
    sendResponse(200, response.toString(), FileSendingDecision.DONT_SEND_FILE);
  }

  public void sendResponse(int statusCode, String responseString, FileSendingDecision decision)
    throws IOException {

    FileInputStream fileInputStream = null;
    final String newLine = "\r\n";
    headers = new LinkedHashMap<String, String>();

    headers.put("Server", "Java HTTPServer");

    if (decision == FileSendingDecision.SEND_FILE) {
      String contentType = responseString.substring(
        responseString.lastIndexOf('.'),
        responseString.length()
      );

      headers.put("Content-Type", contentType);
      fileInputStream = new FileInputStream(responseString);
      headers.put(
        "Content-Length",
        Integer.toString(fileInputStream.available())
      );

    }
    else {
      headers.put("Content-Type", "text/html");
      headers.put("Content-Length", Integer.toString(responseString.length()));
    }

    headers.put("Connection", "close");
    outToClient.writeBytes("HTTP/1.1 " + statusCode + " " + statusCodes.get(statusCode) + newLine);

    for (Map.Entry header: headers.entrySet()) {
      outToClient.writeBytes(header.getKey().toString());
      outToClient.writeBytes(": ");
      outToClient.writeBytes(header.getValue().toString());
      outToClient.writeBytes(newLine);
    }

    outToClient.writeBytes(newLine);

    if (decision == FileSendingDecision.SEND_FILE) {
      logger.info("Headers sent successfully. Sending File now...");
      sendFile(fileInputStream, outToClient);
    }
    else {
      outToClient.writeBytes(responseString);
      logger.info("List of files and folders sent successfully");
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
    logger.info("File sent successfully");
  }

}
