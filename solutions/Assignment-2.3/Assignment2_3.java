/**
 * JAVA code to implement a webserver that can handle basic GET requests.
 * The HTTPServer waits for requests in the main thread and handles the requests
 * in a separate ClientHandler thread.
 */

import httpserver.HttpServer;
import java.io.*;
import java.net.*;
import java.util.*;
import java.util.logging.*;

class Assignment2_3 {

  public static void main(String args[]) throws IOException {
    HttpServer httpServer = new HttpServer(args[0]);
    httpServer.start();
    try {
      Thread.sleep(60);
      httpServer.join();
    } catch (InterruptedException e) {}
 }
  
}
