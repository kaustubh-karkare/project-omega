/**
  * JAVA code to implement a web server that can handle basic GET requests.
  * This is the driver code which uses the httpserver API.
  *
  * A third party package - argparse4j (Command Line Parser) has been used so it must be
  * installed inorder to run the webserver.
  *
  * Four command line arguments(optional) are needed during the execution in the recommended format as shown -
  *   java Assignment2_3 --P PORT_NUMBER --IP IP_ADDRESS --L LOG_CONFIGURATION_FILE_PATH --B BACKLOG
  *
  * PORT_NUMBER is the port on which the server will be hosted.
  *
  * LOG_CONFIGURATION_FILE_PATH is the address of the log configuration file
  * which must be loaded in order to set the logging properties.
  *
  * The HttpServer instance is created using the builder pattern technique with the help of
  * HttpServerBuilder Class
  *
  * Make sure that HttpServer.java, HttpServerBuilder.java and ClientHandler.java
  * are kept in a folder "httpserver" which should be in the current directory of this file.
  */

import httpserver.*;
import java.io.*;
import java.net.*;
import java.util.*;
import java.util.logging.*;
import net.sourceforge.argparse4j.*;
import net.sourceforge.argparse4j.inf.*;

class Assignment2_3 {
  private static final Logger logger = Logger.getLogger(Assignment2_3.class.getName());
  private static int port;
  private static String ipAddress;
  private static int backlog;
  private static String logConfigurationFilePath;

  public static void main(String args[]) throws IOException {

    ArgumentParser parser = ArgumentParsers.newArgumentParser("Server")
      .defaultHelp(true)
      .description("Java Server");

    parser.addArgument("--IP") // Any abbreviation may be used starting with same characters
      .type(String.class)
      .dest("IP")
      .setDefault("127.0.0.1")
      .help("IP Address on which server will be hosted");

    parser.addArgument("--Port")
      .type(Integer.class)
      .setDefault(8080)
      .dest("port")
      .help("Port number on which server will be hosted");

    parser.addArgument("--Backlog")
      .type(Integer.class)
      .setDefault(50)
      .dest("backlog")
      .help("Requested maximum length of the queue of incoming connections");

    parser.addArgument("--LogConfigurationFilePath")
      .type(String.class)
      .dest("configPath")
      .setDefault("")
      .help("Path containing the Configuration File");



    try {
      Namespace namespace = parser.parseArgs(args);
      port = namespace.getInt("port");
      ipAddress = namespace.getString("IP");
      backlog = namespace.getInt("backlog");
      logConfigurationFilePath = namespace.getString("configPath");
      HttpServer httpServer = new HttpServerBuilder()
        .setPort(port)
        .setIP(ipAddress)
        .setBacklog(backlog)
        .setLogConfigurationFilePath(logConfigurationFilePath)
        .getHttpServer();

      httpServer.start();
      try {
        Thread.sleep(60);
        httpServer.join();
      } catch (InterruptedException e) {}

    } catch (ArgumentParserException e) {
      logger.warning(e.getMessage());
    }
  }


}
