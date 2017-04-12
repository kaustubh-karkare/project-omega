/** 
  * Client side code which accepts 2 numbers from the client and sends for operation to the server
  * Type "java Client --help" on the command line to get help about the parameters to be passed  * 
  */
package client;

import java.util.logging.Logger;
import java.util.List;
import net.sourceforge.argparse4j.ArgumentParsers;
import net.sourceforge.argparse4j.inf.ArgumentParser;
import net.sourceforge.argparse4j.inf.ArgumentParserException;
import net.sourceforge.argparse4j.inf.Namespace;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.ObjectOutputStream;
import java.net.Socket;

public class Client {
	private static final Logger logger = Logger.getLogger(Client.class.getName());
	private int selfComputedResult; // to verify the received result
	private String[] input;
	private Socket socket;
	private String ip;
	private int port;
	private Namespace namespace;
	private List<Integer> numbers;

	// Method to validate the answer received from server
	private void validate(String response) {
		selfComputedResult = numbers.get(0) + numbers.get(1);
		logger.info("Answer received from server - " + response);
		int result = Integer.parseInt(response);
		if (result == selfComputedResult) {
			logger.info("Result verified");
		} else {
			logger.warning("Incorrect result obtained");
		}
	}

	public static void main(String[] args) {
		Client client = new Client();
		client.input = new String[2];
		ArgumentParser parser = ArgumentParsers.newArgumentParser("Client")
				.defaultHelp(true);

		parser.addArgument("--ip")
			.type(String.class)
			.dest("ip")
			.setDefault("127.0.0.1")
			.help("IP Address of Server");

		parser.addArgument("--port")
			.type(Integer.class)
			.dest("port")
			.setDefault(8080)
			.help("Port number of server");

		parser.addArgument("--numbers")
			.type(Integer.class)
			.dest("numbers")
			.required(true).nargs(2)
			.help("2 numbers on which operation is to be done");

		try {
			client.namespace = parser.parseArgs(args);
		} catch (ArgumentParserException e) {
			logger.warning(e.getMessage());
			return;
		}

		client.port = client.namespace.getInt("port");
		client.ip = client.namespace.getString("ip");
		client.numbers = client.namespace.getList("numbers");

		try {
			client.socket = new Socket(client.ip, client.port);
			logger.info("Connected to server");
		} catch (IOException | IllegalArgumentException e) {
			logger.warning(e.getMessage());
			return;
		}

		String response = "";
		try {
			ObjectOutputStream oos = new ObjectOutputStream(client.socket.getOutputStream());
			oos.writeObject(client.numbers);
			BufferedReader br = new BufferedReader(new InputStreamReader(client.socket.getInputStream()));
			response = br.readLine();
		} catch (IOException e) {
			logger.warning(e.getMessage());
		}
		client.validate(response);
	}

}
