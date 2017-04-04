package httpserver;

import java.io.*;
import java.net.*;
import java.util.*;
import java.util.logging.*;

// A Webserver waits for clients to connect, then starts a separate thread to handle the request.
public class HttpServer extends Thread {
  private static final LogManager logManager = LogManager.getLogManager();
  private static final Logger logger = Logger.getLogger(HttpServer.class.getName());
  static String logConfigurationFilePath;
  static ServerSocket serverSocket;
  static int port;

  public HttpServer(int port, String logConfigurationFilePath) {
    HttpServer.port = port;
    HttpServer.logConfigurationFilePath = logConfigurationFilePath;
    try {
      initLog();
    } catch (SecurityException | IOException e) {
      logger.warning("Some error occured in loading configuration. Logging through console only");
    }
  }

  // Method to create log file
  public static void initLog() throws SecurityException, IOException {
    // Reading Configuration file which contains predefined instructions regarding logging
    logManager.readConfiguration(new FileInputStream(logConfigurationFilePath));
  }
  // The run() method of HttpServer
  @Override
  public void run() {

    try {
      if (port < 0) {
        throw new NegativeNumberException();
      }
      serverSocket = new ServerSocket(port); // Start,listen on given port
      while (true) {
        try {
          logger.info("Java Server Waiting for client on port " + port);
          Socket socket = serverSocket.accept(); // Wait for a client to connect
          new ClientHandler(socket); // A separate thread to handle each client
        } catch (IOException e) {
          logger.warning(e.getMessage());
        }
      }
    } catch (NegativeNumberException e) {
      logger.warning("Port number should be a positive integer");
    } catch (IOException e) {
      logger.warning("Unable to start server on port " + port);
    }
  }
}

// User defined exception class
class NegativeNumberException extends Exception {
  public NegativeNumberException() {
    super("Port should be a positive integer");
  }
}
