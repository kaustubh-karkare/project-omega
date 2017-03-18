// Server side program to receive 2 arguments from Client and return the sum if possible
import java.io.*;
import java.net.*;

public class Server {
  static ServerSocket serversocket;
  static Socket socket;
  static String[] input;
  // Constructor
  public Server() {
    try {
      serversocket = new ServerSocket(9999); // Trying to setup server on port 9999
    }
    catch(Exception e) {
      System.out.println("Port not available");
      System.exit(0);
    }
  }
  public void start() throws Exception {
    System.out.println("Server started");
    while(true) {
      System.out.println("Waiting for client to connect");
      socket = serversocket.accept(); // Wait for client to get connected
      System.out.println("Client connected");
      Thread.sleep(2000); // Wait for 2 seconds
      getInput();
      sendOutput();
    }
  }
  // Method to get input from client
  public static void getInput() throws Exception {
    ObjectInputStream ois = new ObjectInputStream(socket.getInputStream());
    input = (String[]) ois.readObject();
  }
  // Method to send result to client
  public static void sendOutput() throws Exception {
    OutputStreamWriter osw = new OutputStreamWriter(socket.getOutputStream());
    PrintWriter out = new PrintWriter(osw);
    // In case less or more arguments are received than required
    if(input.length != 2) {
      out.println("Error: Number of arguments should be 2");
      osw.flush();
    }
    else {
      try {
        int number1 = Integer.parseInt(input[0]);
        int number2 = Integer.parseInt(input[1]);
        int ans = number1 + number2;
        out.println(Integer.toString(ans));
        osw.flush();
      }
      // Incase input arguments are not of Integer type
      catch(Exception e) {
        out.println("Error: Arguments not of integer type");
        osw.flush();
      }
    }
  }
  // Main Method
  public static void main(String args[]) throws Exception {
    Server server = new Server();
    server.start();
  }
}
