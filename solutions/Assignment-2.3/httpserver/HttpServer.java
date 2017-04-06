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
  static String ipAddress;
  static int port;
  static int backlog;

  public HttpServer(
    int port,
    String ipAddress,
    int backlog,
    String logConfigurationFilePath
  ) {
    HttpServer.port = port;
    HttpServer.logConfigurationFilePath = logConfigurationFilePath;
    HttpServer.ipAddress = ipAddress;
    HttpServer.backlog = backlog;
    initLog();
  }

  // Method to create log file
  public static void initLog() {
    logger.setLevel(Level.ALL);
    logger.info("Initializing - trying to load configuration file...");
    
    if (logConfigurationFilePath.isEmpty()) {
      logger.warning("Log Configuration File not provided. Logging through console only");
    }
    else {
      Properties preferences = new Properties();
      try {
        FileInputStream configFile = new FileInputStream(logConfigurationFilePath);
        preferences.load(configFile);
        logManager.readConfiguration(configFile);
      } catch (IOException e) {
        logger.warning("Some error occured in loading configuration. Logging through console only");
      }
    }
  }

  // The run() method of HttpServer
  @Override
  public void run() {
    try {
      serverSocket = new ServerSocket(port, backlog, InetAddress.getByName(ipAddress));
      while (true) {
        try {
          logger.info("Java Server Waiting for client on port " + port);
          Socket socket = serverSocket.accept(); // Wait for a client to connect
          new ClientHandler(socket); // A separate thread to handle each client
        } catch (IOException e) {
          logger.warning(e.getMessage());
        }
      }
    } catch (IOException e) {
      logger.warning("Unable to start server on address: " + ipAddress + ":" + port);
    } catch (IllegalArgumentException e) {
      logger.warning("Port number can't be a negative integer.");
    }
  }
}
