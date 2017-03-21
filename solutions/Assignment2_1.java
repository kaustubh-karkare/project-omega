/*JAVA program to implement Multiple client-server interaction
 *Multithreading approach is used where Server and Clients run as separate threads
 *Server has an additional ClientServiceThread which processes the requests of the clients
 *The Server accepts requests from Clients and passes the requests to ClientServiceThread
 *All messages are recorded in a LOG File
 */
import java.io.*;
import java.net.*;
import java.util.*;
import java.util.logging.*;

// Server class
class Server extends Thread {
  private static final Logger logger = Logger.getLogger(Server.class.getName());
  static int port;
  static ServerSocket serverSocket;
  static Socket socket;
  // Constructor
  public Server(int port) throws Exception {
      Server.port = port;
      serverSocket = new ServerSocket(port);
    }
  @Override
  public void run() {
    logger.log(Level.INFO, "Server Started");
    while (true) {
      logger.log(Level.INFO, "Waiting for client to connect");
      try {
        socket = serverSocket.accept();
      } catch(Exception e) {}
      logger.log(Level.INFO, "Client connected");
      ClientServiceThread worker = new ClientServiceThread(socket);
      worker.start();
    }
  }
}

// Class which is responsible for processing Client request
class ClientServiceThread extends Thread {
  Socket socket;
  //Constructor
  public ClientServiceThread(Socket socket) {
    this.socket = socket;
  }
  @Override
  public void run() {
    try {
      Thread.sleep(2000); // Wait for 2 seconds
    } catch(Exception e) {}
    try {
      String[] input; // Input received from Client
      String reply; // Reply to be sent to Client
      input = fetchClientRequest();
      reply = processData(input);
      replyClient(reply);
    } catch(Exception e) {}
  }
  // Method to fetch data from client
  String[] fetchClientRequest() throws Exception {
    ObjectInputStream ois = new ObjectInputStream(socket.getInputStream());
    String[] input = (String[]) ois.readObject();
    return input;
  }
  // Method to process the received data
  String processData(String[] input) throws Exception {
    // In case less or more arguments are received than required
    String reply;
    if (input.length != 2)
    reply = "Error: Number of arguments should be 2";
    else {
      try {
        int number1 = Integer.parseInt(input[0]);
        int number2 = Integer.parseInt(input[1]);
        int ans = number1 + number2;
        reply = Integer.toString(ans);
      }
      // In case input arguments are not of integer type
      catch(Exception e) {
        reply = "Error: Arguments not of integer type";
      }
    }
    return reply;
  }
  // Method to send feedback to client
  void replyClient(String reply) throws Exception {
    OutputStreamWriter osw = new OutputStreamWriter(socket.getOutputStream());
    PrintWriter out = new PrintWriter(osw);
    out.println(reply);
    osw.flush();
  }
}

// Client class
class Client extends Thread {
  private static final Logger logger = Logger.getLogger(Client.class.getName());
  int selfComputedResult; // to verify received result
  String[] arguments; // input from user
  Socket socket;
  int clientID;
  // Constructor
  public Client(String IP, int port, String[] input, int clientID) throws Exception {
    socket = new Socket(IP, port);
    arguments = input;
    this.clientID = clientID;
  }
  @Override
  public void run() {
    String response = null;
    try {
      queryServer();
      response = getResponse();
    } catch(Exception e) {}
    validate(response);
  }
  // Method to send client data to server
  public void queryServer() throws Exception {
    ObjectOutputStream oos = new ObjectOutputStream(socket.getOutputStream());
    oos.writeObject(arguments);
  }
  // Method to receive response from server
  public String getResponse() throws Exception {
    BufferedReader br =
    new BufferedReader(new InputStreamReader(socket.getInputStream()));
    String response = br.readLine();
    return response;
  }
  // Method to validate the answer recieved from server
  public void validate(String response) {
    try {
      selfComputedResult = Integer.parseInt(arguments[0]) + Integer.parseInt(arguments[1]);
    } catch(Exception e) {}
    if (response.startsWith("Error:")) {
      logger.log(Level.WARNING, "Client "+clientID+": Error message from server side - "+response);
    }
    else {
      logger.log(Level.INFO, "Client "+clientID+": Answer received from server: "+response);
      int result = Integer.parseInt(response);
      if (result == selfComputedResult) {
        logger.log(Level.FINE, "Client "+clientID+": Result verified");
      }
      else {
        logger.log(Level.WARNING, "Client "+clientID+": Incorrect result obtained");
      }
    }
  }
}

// Class containing the main method
class Assignment2_1 {
  private final static Logger logger = Logger.getLogger(Assignment2_1.class.getName());
  private static FileHandler fh = null;
  static int port;
  static Server server;
  static int clientsCount;
  static Client[] client;
  static String[] input;
  // Method to create log file
  public static void initLog() {
    try {
      fh = new FileHandler("Status.log", false);
    }
    catch (SecurityException | IOException e) {
      e.printStackTrace();
    }
    Logger l = Logger.getLogger("");
    fh.setFormatter(new SimpleFormatter());
    l.addHandler(fh);
    l.setLevel(Level.FINE);
  }
  // Main method
  public static void main(String args[]) {
    initLog();
    Scanner scanner = new Scanner(System.in);
    System.out.println("Enter the number of clients");
    clientsCount = scanner.nextInt();
    client = new Client[clientsCount];
    // Trying to set up the server
    System.out.println("Enter port on which server has to be hosted");
    port = scanner.nextInt();
    try {
      server = new Server(port);
    }
    catch(Exception e) {
      logger.log(Level.WARNING, "Server cannot be hosted on port "+port);
      System.exit(0);
    }
    server.start();
    // Trying to connect client to server one by one after taking input from user
    for (int i = 0; i < clientsCount; i++) {
      System.out.println("Enter 2 numbers for client "+(i+1));
      if (i == 0) {
        scanner.nextLine(); // To compensate for new line character for 1st input
      }
      String inputString = scanner.nextLine();
      input = inputString.split(" ");
      try {
        client[i] = new Client("127.0.0.1", port, input,i+1);
      }
      catch(Exception e) {
        logger.log(Level.WARNING, "Client "+(i+1)+" cannot connect to server");
      }
      client[i].start();
    }
    logger.log(Level.INFO, "All clients served");
  }
}
