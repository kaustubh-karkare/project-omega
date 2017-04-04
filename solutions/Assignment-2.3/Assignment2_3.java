/**
  * JAVA code to implement a web server that can handle basic GET requests.
  * This is the driver code which uses the httpserver API.
  *
  * A third party package - argparse4j (Command Line Parser) has been used so it must
  * installed inorder to run the webserver.
  *
  * Two command line arguments are needed during the execution in the recommended format as shown -
  *   java Assignment2_3 --P PORT_NUMBER --L LOG_CONFIGURATION_FILE_PATH
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

  public static void main(String args[]) throws IOException {
    int port;
    String logConfigurationFilePath;
    ArgumentParser parser = ArgumentParsers.newArgumentParser("Server")
      .defaultHelp(true)
      .description("Java Server");

    parser.addArgument("--Port") // Any abbreviation may be used starting with same characters
            .type(Integer.class)
            .setDefault(8080)
            .dest("port")
            .help("Port number on which server will be hosted");

    parser.addArgument("--LogConfigurationFilePath") // Same rule for abbreviation
            .type(String.class)
            .dest("configPath")
            .help("Path containing the Configuration File");

    try {
      Namespace namespace = parser.parseArgs(args);
      port = namespace.getInt("port");
      logConfigurationFilePath = namespace.getString("configPath");
      HttpServer httpServer = new HttpServerBuilder()
                                          .setPort(port)
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
