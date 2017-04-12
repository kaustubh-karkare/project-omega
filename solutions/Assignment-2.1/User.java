/**
  * Server side code which is managed by a user.
  * It uses the server package (API) to create a server to perform a certain operation.
  * The user can create his own logic function and pass it to the server.
  * Type "java User --help" on the command line to get help about the parameters to be passed.
  */
import java.lang.reflect.Method;
import java.util.logging.Logger;
import net.sourceforge.argparse4j.ArgumentParsers;
import net.sourceforge.argparse4j.inf.ArgumentParser;
import net.sourceforge.argparse4j.inf.ArgumentParserException;
import net.sourceforge.argparse4j.inf.Namespace;
import server.Server;
import server.ServerBuilder;

public class User {

	private final static Logger logger = Logger.getLogger(User.class.getName());
	private static int port;
	private static int backlog;
	private static String ip;
	private static Namespace namespace;
	private static Server server;
	private static Method logicFunction;
	
	// Logic function to be passed to the server 
	public String logicFunction(int number1, int number2) {
		int answer = number1 + number2;
		return (Integer.toString(answer));
	}

	public static void main(String[] args) {
		ArgumentParser parser = ArgumentParsers
				.newArgumentParser("User")
				.defaultHelp(true);

		parser.addArgument("--ip")
			.type(String.class)
			.dest("ip")
			.setDefault("127.0.0.1")
			.help("IP Address of server");

		parser.addArgument("--port")
			.type(Integer.class)
			.dest("port")
			.setDefault(8080)
			.help("Port number on which server is to be hosted");

		parser.addArgument("--backlog")
			.type(Integer.class)
			.dest("backlog")
			.setDefault(50)
			.help("maximum incoming client connection requests to be stored in queue");

		try {
			namespace = parser.parseArgs(args);
		} catch (ArgumentParserException e) {
			logger.warning(e.getMessage()); // In case invalid arguments are provided
			return;
		}

		port = namespace.getInt("port");
		ip = namespace.getString("ip");
		backlog = namespace.getInt("backlog");

		// Creating Method object of Logic Function to be passed to the server
		Class[] parameterTypes = new Class[2];
		parameterTypes[0] = int.class;
		parameterTypes[1] = int.class;
		try {
			logicFunction = User.class.getMethod("logicFunction", parameterTypes);
		} catch (NoSuchMethodException | SecurityException e) {
			logger.warning(e.getMessage());
		}

		// Initializing the server
		try {
			User user = new User();
			server = new ServerBuilder()
					.setPort(port)
					.setIP(ip)
					.setBacklog(backlog)
					.setLogicFunction(logicFunction)
					.setUserObject(user)
					.getServer();
		} catch (Exception e) {
			logger.warning("Server cannot be hosted on address - " + ip + ":" + port);
			return;
		}
		
		// Starting server thread
		server.start();
		try {
			server.join();
		} catch (InterruptedException e) {
			logger.warning(e.getMessage());
		}
	}
}
