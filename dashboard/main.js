// D3.js Commit Visualization
d3.json("../graphql_output.json").then(data => {
  const svg = d3.select("#chart");
  const commits = data.viewer.repositories.nodes.map((d, i) => ({ x: i * 100 + 50, y: 200, name: d.name }));

  svg.selectAll("circle")
    .data(commits)
    .enter()
    .append("circle")
    .attr("cx", d => d.x)
    .attr("cy", d => d.y)
    .attr("r", 20)
    .style("fill", "steelblue");

  svg.selectAll("text")
    .data(commits)
    .enter()
    .append("text")
    .attr("x", d => d.x)
    .attr("y", d => d.y + 40)
    .attr("text-anchor", "middle")
    .text(d => d.name);
});
