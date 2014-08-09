'use strict';

var pathsData = [
    {src: 12, dst: 98, type: "ladder"},
    {src: 32, dst: 62, type: "ladder"},
    {src: 42, dst: 68, type: "ladder"},
    {src: 95, dst: 25, type: "snake"},
    {src: 21, dst: 3, type: "snake"}
];

var drawBoard = function (pathsData) {
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


    cells.attr("width", cellWidth)
        .attr("height", cellWidth)
        .attr("x", function (d) {
            return (d % cellsInRow) * cellWidth;
        })
        .attr("y", function (d) {
            return Math.floor(d / cellsInRow) * cellWidth;
        })
        .style("stroke", "gray")
        .style("stroke-width", 2)
        .style("fill", "#FFEFD5");


    var getX = function (cellNumber) {
        var pos = (cellNumber % cellsInRow) * cellWidth + (cellWidth / 2);
        if (Math.floor(cellNumber / cellsInRow) % 2 == 0) {
            return pos;
        } else {
            return boardWidth - pos;
        }
    }

    var getXSrc = function (path) {
        return getX(path.src - 1);
    }

    var getXDst = function (path) {
        return getX(path.dst - 1);
    }

    var getYSrc = function (path) {
        return getY(path.src - 1);
    }

    var getYDst = function (path) {
        return getY(path.dst - 1);
    }

    var getY = function (cellNumber) {
        return boardWidth - Math.floor(cellNumber / cellsInRow) * cellWidth + (cellWidth / 3 * 2) - cellWidth;
    }


    var labels = board.selectAll("text")
        .data(cellLabels)
        .enter()
        .append("text");


    var textAttributes = labels
        .text(function (d) {
            return d + 1;
        })
        .attr("x", getX)
        .attr("y", getY)
        .style("fill", "black")
        .style("font-size", labelFontSize)
        .style("text-anchor", "middle");


    var paths = board.selectAll("line")
        .data(pathsData)
        .enter()
        .append("line");


    paths.attr("x1", getXSrc)
        .attr("y1", getYSrc)
        .attr("x2", getXDst)
        .attr("y2", getYDst)
        .style("stroke", function (path) {
            return path.type == "ladder" ? "FF0086" : "3B916A";
        })
        .style("stroke-dasharray", function (path) {
            return path.type == "ladder" ? "2" : "1";
        })
        .style("stroke-width", 10);
}


if (location.pathname.match(/^\/boards\/\d+$/)) {
    var boardDataUrl = "/api/boards/" + _.last(location.pathname.split("/"));

    $.get(boardDataUrl, function (data) {
        var ls = _.map(data.ladders, function (l) {
            l.type = "ladder";
            return l;
        });
        var ss = _.map(data.snakes, function (l) {
            l.type = "snake";
            return l;
        });

        drawBoard(ls.concat(ss));
    });
}
