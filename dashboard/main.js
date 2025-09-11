// Example: D3.js commit timeline
fetch('../github_repo_data.json')
.then(response => response.json())
.then(data => {
  const commits = data.data.repository.object.history.nodes;
  const width = 800, height = 400;
  const svg = d3.select("#commit-timeline")
    .append("svg").attr("width", width).attr("height", height);

  const parseDate = d3.isoParse;
  const x = d3.scaleTime()
    .domain(d3.extent(commits, d => parseDate(d.committedDate)))
    .range([50, width-50]);

  const y = d3.scaleLinear()
    .domain([0, commits.length])
    .range([height-50, 50]);

  svg.selectAll("circle")
    .data(commits)
    .enter()
    .append("circle")
    .attr("cx", d => x(parseDate(d.committedDate)))
    .attr("cy", (d,i) => y(i))
    .attr("r", 5)
    .attr("fill", "steelblue")
    .append("title")
    .text(d => d.message);
});
