/**
  * JAVA program to download a file from a URL.
  * Type "java Assignment2_2 --help" on the command line for usage details.
  * This is the driver code which uses the "downloader" package.
  * Here, a instance of FileDownloader class is created which receives the URL and the Thread Count.
  * Finally, the downloading process starts in a separate thread.
  */
import java.util.logging.Logger;
import downloader.FileDownloader;
import net.sourceforge.argparse4j.ArgumentParsers;
import net.sourceforge.argparse4j.inf.ArgumentParser;
import net.sourceforge.argparse4j.inf.ArgumentParserException;
import net.sourceforge.argparse4j.inf.Namespace;

public class Assignment2_2 {
	private final static Logger logger =
		Logger.getLogger(Assignment2_2.class.getName());
	private static String url;
	private static int threadCount;
	private static Namespace namespace;
	private static FileDownloader fileDownloader;

	public static void main(String[] args) {
		ArgumentParser parser = ArgumentParsers
			.newArgumentParser("Downloader")
			.defaultHelp(true);

		parser.addArgument("--url")
			.type(String.class)
			.dest("url")
			.required(true)
			.help("URL of the file to be downloaded");

		parser.addArgument("--threads")
			.type(Integer.class)
			.dest("threads")
			.setDefault(4)
			.help("Number of threads which will download the file");

		try {
			namespace = parser.parseArgs(args);
		} catch (ArgumentParserException e) {
			logger.warning(e.getMessage());
			return;
		}

		url = namespace.getString("url");
		threadCount = namespace.getInt("threads");
		// Initiate downloading
		fileDownloader = new FileDownloader(url, threadCount);

		try {
			fileDownloader.join(); // Wait for downloading to finish
		} catch (InterruptedException e) {
			logger.warning(e.getMessage());
		}
	}
}
