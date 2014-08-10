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

Solution Approach
-----------------

* For a given combination of snakes and ladders, create a single node with a label `board` in Neo4J and associate information about snakes and ladders as a metadata (technically, strings in Hackerrank's format associated with node properties). This is my 2nd attempt and a dirty hack, cause initial implementation which stored the whole board as a graph had 3 problems:
** Free version of GrapheneDB allows only 1K nodes and 10K relations for free and in my case each board required 100 nodes and several hundreds of relations.
** Querying a lot of nodes without creating an index is slow
** py2neo has an interesting way of working with database which for bulk requests were slow (see more details in "Lessons Learned" section)
* To solve a board, do the following steps:
** Create a temporary set do nodes and relations which represents a board with snakes and ladders as a graph
** Call Dijkstra's algorithm on them and collect results
** Remove temporary data
* To draw a board, to the following:
** Create an in-memory board representation
** Send it to front-end as a JSON
** Bind this data to D3.js-defined `<svg>` element

*Graph Representation*

The whole board is represented as a graph with cells being nodes, jumps (either dice rolls, snakes or ladders) being edges with a weight. Note that for the sake of Dijkstra's correct execution, edge costs should be non-negative. I made the following assumption:

* All dice rolls will lead to edges with weights in a range from 1 to 6
* All ladders should have a weight of 0 (player's chip will be automatically moved to the end of the ladder with no cost)
* All snakes is a tax to our movement, which means that their cost can be calculated as `destination - source`

*Sample Graph*

This is a subset of a graph representing a board with a ladder from 2 to 20 and a snake from 8 to 1.


![Sample Graph](https://chart.googleapis.com/chart?chl=digraph+G+%7B%0D%0A++1+-%3E+2+%5Blabel%3D%22cost%3A1%22%5D%3B%0D%0A++1+-%3E+3+%5Blabel%3D%22cost%3A2%22%5D%3B%0D%0A++1+-%3E+4+%5Blabel%3D%22cost%3A3%22%5D%3B%0D%0A++1+-%3E+5+%5Blabel%3D%22cost%3A4%22%5D%3B%0D%0A++1+-%3E+6+%5Blabel%3D%22cost%3A5%22%5D%3B%0D%0A++1+-%3E+7+%5Blabel%3D%22cost%3A6%22%5D%3B%0D%0A++2+-%3E+3+%5Blabel%3D%22cost%3A1%22%5D%3B%0D%0A++2+-%3E+4+%5Blabel%3D%22cost%3A2%22%5D%3B%0D%0A++2+-%3E+5+%5Blabel%3D%22cost%3A3%22%5D%3B%0D%0A++2+-%3E+6+%5Blabel%3D%22cost%3A4%22%5D%3B%0D%0A++2+-%3E+7+%5Blabel%3D%22cost%3A5%22%5D%3B%0D%0A++2+-%3E+8+%5Blabel%3D%22cost%3A6%22%5D%3B%0D%0A++2+-%3E+20+%5Blabel%3D%22cost%3A0%5Cntype%3Aladder%22%5D%3B%0D%0A++8+-%3E+1+%5Blabel%3D%22cost%3A7%5Cntype%3Asnake%22%5D%3B%0D%0A%7D%0D%0A++++++++&cht=gv)

