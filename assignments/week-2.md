## Problem 2.1

Using the basic socket library for your preferred language, create a TCP server & client.

- The server listens on a given port, waiting for a client to connect.
- The client connects to the server via the above port, and sends 2 numbers, separated by a space.
- The server receives the message, waits for 2 seconds, and then responds with the sum of the 2 numbers.
- The client gets the result, verifies that it is correct, and then ends.
- The server continues waiting for other clients.

## Problem 2.2

Write a program that takes a URL as input, and downloads the file into the current directory. You are still only allowed to use the basic socket library like in the previous assignment. As a result of that restriction, you will need to study the [HTTP protocol](https://www.httpwatch.com/httpgallery/introduction/), and figure how to make the necessary request.
