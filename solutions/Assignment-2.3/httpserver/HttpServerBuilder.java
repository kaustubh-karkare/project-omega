package httpserver;
import httpserver.HttpServer;

// Builder class of HttpServer class
public class HttpServerBuilder {
  private int port;
  private int backlog;
  private String ipAddress;
  private String logConfigurationFilePath;

  public HttpServerBuilder setPort(int port) {
    this.port = port;
    return this;
  }

  public HttpServerBuilder setIP(String ipAddress) {
    this.ipAddress = ipAddress;
    return this;
  }

  public HttpServerBuilder setBacklog(int backlog) {
    this.backlog = backlog;
    return this;
  }

  public HttpServerBuilder setLogConfigurationFilePath(String logConfigurationFilePath) {
    this.logConfigurationFilePath = logConfigurationFilePath;
    return this;
  }

  public HttpServer getHttpServer() {
    return new HttpServer(port, ipAddress, backlog, logConfigurationFilePath);
  }
}
