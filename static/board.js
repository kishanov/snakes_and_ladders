'use strict';

console.log("hello");

var cellsCount = 100;
var cellsInRow = 10;
var cellWidth = 40;
var boardWidth = cellsInRow * cellWidth;
var labelFontSize = cellWidth / 2;


var board = d3.select("#game-board")
    .append("svg")
    .attr("width", boardWidth)
    .attr("height", boardWidth);


var cellLabels = _.range(cellsCount);
var cells = board.selectAll("rect")
    .data(cellLabels)
    .enter()
    .append("rect");


var rectAttributes = cells
    .attr("width", cellWidth)
    .attr("height", cellWidth)
    .attr("x", function (d) {
        return (d % cellsInRow) * cellWidth;
    })
    .attr("y", function (d) {
        return Math.floor(d / cellsInRow) * cellWidth;
    })
    .style("stroke", "black")
    .style("stroke-width", 3)
    .style("opacity", 0.5)
    .style("fill", "crimson");


var labels = board.selectAll("text")
    .data(cellLabels)
    .enter()
    .append("text");


var textAttributes = labels
    .text(function (d) {
        console.log(d);
        return d + 1;
    })
    .attr("x", function (d) {
        var pos = (d % cellsInRow) * cellWidth + (cellWidth / 2);
        if (Math.floor(d / cellsInRow) % 2 == 0) {
            return pos;
        } else {
            return boardWidth - pos;
        }
    })
    .attr("y", function (d) {
        return boardWidth - Math.floor(d / cellsInRow) * cellWidth + (cellWidth / 3 * 2) - cellWidth;
    })
    .style("fill", "black")
    .style("font-size", labelFontSize)
    .style("text-anchor", "middle");
