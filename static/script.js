fetch("static/projects.json")
  .then((response) => response.json())
  .then((projects) => {
    const container = document.getElementById("projects-container");
    container.innerHTML = ""; // Clear loading text

    projects.forEach((project) => {
      const div = document.createElement("div");
      div.className = "project";
      div.innerHTML = `
        <h3>${project.name}</h3>
        <p>${project.description}</p>
        <p><strong>Start:</strong> ${project.start_date} &nbsp; | &nbsp; <strong>End:</strong> ${project.end_date}</p>
        <a href="${project.github_link}" class="btn" target="_blank">View on GitHub</a>
      `;
      container.appendChild(div);
    });
  })
  .catch((error) => {
    document.getElementById("projects-container").innerHTML = "<p>Failed to load projects.</p>";
    console.error("Error loading projects:", error);
  });
