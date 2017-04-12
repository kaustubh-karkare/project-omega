/**
  * Implementation of server API.
  * Server has an additional ClientServiceThread which processes the requests of the clients.
  * The Server accepts requests from Clients and passes the requests to ClientServiceThread.
  * The ClientServiceThread processes the requests and sends response to the respective Clients.
  */
package server;

import java.util.List;
import java.util.logging.Logger;
import java.io.IOException;
import java.io.ObjectInputStream;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.net.InetAddress;
import java.net.ServerSocket;
import java.net.Socket;

public class Server extends Thread {
	private static final Logger logger = Logger.getLogger(Server.class.getName());
	private Method logicFunction;
	private int port;
	private String ip;
	private int backlog;
	private ServerSocket serverSocket;
	private Socket socket;
	private Object userObject;

	public Server(int port, String ip, int backlog, Method logicFunction, Object userObject) throws IOException {
		this.port = port;
		this.ip = ip;
		this.backlog = backlog;
		this.logicFunction = logicFunction;
		this.userObject = userObject;
		serverSocket = new ServerSocket(port, backlog, InetAddress.getByName(ip));
	}

	@Override
	public void run() {
		logger.info("Server started");
		while (true) {
			logger.info("Waiting for Client to connect");
			try {
				socket = serverSocket.accept();
			} catch (IOException e) {}
			logger.info("Client connected - " + socket.getInetAddress() + ":" + socket.getPort());
			ClientServiceThread worker = new ClientServiceThread(socket, logicFunction, userObject);
			worker.start();
		}
	}
}

// Class which is responsible for processing Client request
class ClientServiceThread extends Thread {
	private static final Logger logger = Logger.getLogger(ClientServiceThread.class.getName());
	private Socket socket;
	private Method logicFunction;
	private Object userObject;

	public ClientServiceThread(Socket socket, Method logicFunction, Object userObject) {
		this.socket = socket;
		this.logicFunction = logicFunction;
		this.userObject = userObject;
	}

	@Override
	public void run() {
		try {
			logger.info("Waiting for 2 seconds");
			Thread.sleep(2000);
		} catch (InterruptedException e) {}

		List<Integer> input; // Input received from client
		String reply; // Reply to be sent to Client
		try {
			ObjectInputStream ois = new ObjectInputStream(socket.getInputStream());
			input = (List<Integer>) ois.readObject();
			logger.info("Input received from Client");
			// Processing Client Request
			reply = processData(input, userObject);
			OutputStreamWriter osw = new OutputStreamWriter(socket.getOutputStream());
			PrintWriter out = new PrintWriter(osw);
			out.println(reply);
			osw.flush();
			logger.info("Response sent to Client");
		} catch (IOException | ClassNotFoundException e) {
			logger.warning(e.getMessage());
		}
	}

	// Method to process the received data
	String processData(List<Integer> input, Object userObject) {
		String reply = "";
		Object[] parameters = new Object[2];
		parameters[0] = input.get(0);
		parameters[1] = input.get(1);
		try {
			reply = logicFunction.invoke(userObject, parameters).toString();
		} catch (IllegalAccessException | IllegalArgumentException | InvocationTargetException e) {
			logger.warning(e.getMessage());
		}
		return reply;
	}

}
