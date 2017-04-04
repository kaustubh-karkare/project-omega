package httpserver;
import httpserver.HttpServer;

// Builder class of HttpServer class
public class HttpServerBuilder {
  private int port;
  private String logConfigurationFilePath;

  public HttpServerBuilder setPort(int port) {
    this.port = port;
    return this;
  }

  public HttpServerBuilder setLogConfigurationFilePath(String logConfigurationFilePath) {
    this.logConfigurationFilePath = logConfigurationFilePath;
    return this;
  }

  public HttpServer getHttpServer() {
    return new HttpServer(port, logConfigurationFilePath);
  }
}
