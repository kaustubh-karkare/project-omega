
## Practice Problem 1

- Take a screenshot of your Facebook newsfeed. Reproduce it from scratch using only HTML & CSS (no JavaScript).
- Do not use any external libraries / stylesheets. It doesn't have to be pixel-perfect, since there is a point of diminishing returns, but the goal here is to teach you enough HTML such that you can understand the page source for a website when you need to.

## Practice Problem 2

- Install [MySQL](https://www.mysql.com/) and [Memcached](https://memcached.org/) on your system.
- Connect to these services using client libraries in the language of your choice.

## Graded Assignment

- Create a basic website that allows you to manage a to-do list.
- The user should be able to create an account. The username, password and other information should be stored in a MySQL database.
- The user should be able to login, and logout. The current login status should be stored in a cookie. The server validates the cookie by checking it against information stored in Memcache.
- While logged in, the user can items to the to-do list. These items are also stored in the database.
