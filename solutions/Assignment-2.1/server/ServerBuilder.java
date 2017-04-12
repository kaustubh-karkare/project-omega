// Server Builder class

package server;

import java.io.IOException;
import java.lang.reflect.Method;

public class ServerBuilder {
	private int port;
	private int backlog;
	private String ip;
	private Method logicFunction;
	private Object userObject;
	
	public ServerBuilder setPort(int port) {
		this.port = port;
		return this;
	}
	
	public ServerBuilder setIP(String ip) {
		this.ip = ip;
		return this;
	}
	
	public ServerBuilder setBacklog(int backlog) {
		this.backlog = backlog;
		return this;
	}
	
	public ServerBuilder setLogicFunction(Method logicFunction) {
		this.logicFunction = logicFunction;
		return this;
	}
	
	public ServerBuilder setUserObject(Object userObject) {
		this.userObject = userObject;
		return this;
	}
	
	public Server getServer() throws IOException {
		return new Server(port, ip, backlog, logicFunction, userObject);
	}	

}
