## Problem 2.1

Using the basic socket library for your preferred language, create a TCP server & client.

- The server listens on a given port, waiting for a client to connect.
- The client connects to the server via the above port, and sends 2 numbers, separated by a space.
- The server receives the message, waits for 2 seconds, and then responds with the sum of the 2 numbers.
- The client gets the result, verifies that it is correct, and then ends.
- The server continues waiting for other clients.

## Problem 2.2

Using the same basic socket library as the previous assignment, write a program that takes a URL as input, and downloads the file into the current directory.

Since you're not allowed to use Python's `urllib` module, JavaScript's `http` module, or any other similar ones, you will need to study the [HTTP protocol](https://www.httpwatch.com/httpgallery/introduction/), and figure how to make the necessary request.

## Problem 2.3

Using the same basic socket library as the previous assignment, implement a webserver that can handle basic `GET` requests.
- If the requested path is a directory, check to see if there is an `index.html` file in that directory, and return that. If not, generate a list of files and return those instead.
- If the requested path is a file, check to see if it actually exists in a given directory. If yes, provide that, or else return a `404` error.
