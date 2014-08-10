About
=====

This project is a web application, which is loosely based on [Hackerranks' Snakes and Ladders: The Quickest Way Up](https://www.hackerrank.com/challenges/the-quickest-way-up) problem using [Neo4J's built-in Dijkstra algorithm](http://docs.neo4j.org/chunked/stable/rest-api-graph-algos.html#rest-api-execute-a-dijkstra-algorithm-and-get-a-single-path).

Technology Stack
----------------

* *Database*: [Neo4J](http://www.neo4j.org/)
* *Game Engine*: Python 2.7, using [Py2neo](http://nigelsmall.com/py2neo/1.6/) library to work with Neo4J
* *Web App*: [Flask](http://flask.pocoo.org/) with [Flask-WTF](https://flask-wtf.readthedocs.org/en/latest/) for forms processing and [Jinja2](http://jinja.pocoo.org/docs/) for server-side temlpating
* *Front-end*: [D3.js](http://d3js.org/) for field rendering (using HTML SVG) with [JQuery](http://jquery.com/) for basic AJAX and DOM manipulation and [Lo-Dash](http://lodash.com/) just in case.
* *Deployment*: [Heroku](https://devcenter.heroku.com/articles/getting-started-with-python) with [GrapheneDB](http://www.graphenedb.com/) add-on for persistence.

