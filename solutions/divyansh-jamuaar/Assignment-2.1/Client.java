/* Client side program to scan 2 numbers as Command Line Arguments,
 * send them to the server, receive the result and verify it's correctness
 */
import java.io.*;
import java.net.*;

public class Client {
  int self_computed_result; // To verify received result
  String ip_address = "localhost"; // IP of server
  int port = 9999;  // Port on which server is hosted
  Socket socket;
  // Constructor
  public Client() {
    try {
      socket = new Socket(ip_address,port);
    }
    catch(Exception e) {
      System.out.println("Connection refused by server or no server found");
      System.exit(0);
    }
  }
  // Method to compute result on client side
  public void computeResult(String args[]) {
    try {
      int number1 = Integer.parseInt(args[0]);
      int number2 = Integer.parseInt(args[1]);
      self_computed_result = number1 + number2;
    }
    catch(Exception e) {}
  }
  // Method to send data to server
  public void sendData(String args[]) throws Exception {
    ObjectOutputStream oos = new ObjectOutputStream(socket.getOutputStream());
    oos.writeObject(args);
  }
  // Method to receive result from server and verify it's correctness
  public void getData() throws Exception {
    BufferedReader br =
    new BufferedReader(new InputStreamReader(socket.getInputStream()));
    String input_result = br.readLine();
    // If Server returns some Error message
    if(input_result.startsWith("Error:")) {
      System.out.println("Message from server side: " + input_result);
    }
    else {
        System.out.println("Result received from server: " + input_result);
        int result = Integer.parseInt(input_result);
        if(result == self_computed_result) {
          System.out.println("Result verified");
        }
        else {
          System.out.println("Incorrect result obtained");
        }
    }
  }
  // Main method
  public static void main(String args[]) throws Exception {
    Client client = new Client();
    client.computeResult(args);
    client.sendData(args);
    client.getData();
  }

}
