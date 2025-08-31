// Mobile menu toggle
function toggleMenu() {
  const menu = document.getElementById('nav-menu');
  menu.classList.toggle('active');
}

// Active navigation highlighting
function updateActiveNav() {
  const sections = document.querySelectorAll('section[id]');
  const navLinks = document.querySelectorAll('.nav-link');
  
  let current = '';
  sections.forEach(section => {
    const sectionTop = section.offsetTop - 100;
    if (window.pageYOffset >= sectionTop) {
      current = section.getAttribute('id');
    }
  });

  navLinks.forEach(link => {
    link.classList.remove('active');
    if (link.getAttribute('href') === '#' + current) {
      link.classList.add('active');
    }
  });
}

// Scroll animations
function handleScrollAnimations() {
  const elements = document.querySelectorAll('.fade-in');
  elements.forEach(element => {
    const elementTop = element.getBoundingClientRect().top;
    const elementVisible = 150;
    
    if (elementTop < window.innerHeight - elementVisible) {
      element.classList.add('visible');
    }
  });
}

// Load projects with enhanced styling
function loadProjects() {
  fetch("/static/projects.json")
    .then((response) => response.json())
    .then((projects) => {
      const container = document.getElementById("projects-container");
      container.innerHTML = "";

      projects.forEach((project, index) => {
        const projectCard = document.createElement("div");
        projectCard.className = "project-card";
        projectCard.style.animationDelay = `${index * 0.1}s`;
        
        projectCard.innerHTML = `
          <div class="project-header">
            <h3 class="project-title">${project.name}</h3>
            <span class="project-duration">${project.start_date} - ${project.end_date}</span>
          </div>
          <p class="project-description">${project.description}</p>
          <div class="project-footer">
            <a href="${project.github_link}" class="project-link" target="_blank">
              <i class="fab fa-github"></i>
              View on GitHub
            </a>
          </div>
        `;
        
        container.appendChild(projectCard);
      });
    })
    .catch((error) => {
      const container = document.getElementById("projects-container");
      container.innerHTML = `
        <div style="text-align: center; color: var(--text-secondary); padding: 2rem;">
          <i class="fas fa-exclamation-triangle" style="font-size: 2rem; margin-bottom: 1rem; color: var(--accent);"></i>
          <p>Failed to load projects. Please try again later.</p>
        </div>
      `;
      console.error("Error loading projects:", error);
    });
}

// Event listeners
window.addEventListener('scroll', () => {
  updateActiveNav();
  handleScrollAnimations();
});

window.addEventListener('load', () => {
  loadProjects();
  handleScrollAnimations();
});

// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
    e.preventDefault();
    const target = document.querySelector(this.getAttribute('href'));
    if (target) {
      target.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      });
    }
    
    // Close mobile menu if open
    const menu = document.getElementById('nav-menu');
    menu.classList.remove('active');
  });
});

// Add staggered loading animation to hero elements
document.addEventListener('DOMContentLoaded', function() {
  const heroElements = document.querySelectorAll('.hero-content > *');
  heroElements.forEach((element, index) => {
    element.style.opacity = '0';
    element.style.transform = 'translateY(30px)';
    element.style.animation = `fadeInUp 0.8s ease ${index * 0.2}s forwards`;
  });

  // Initialize scroll animations on page load
  setTimeout(handleScrollAnimations, 100);
});

// Add intersection observer for better performance on scroll animations
if ('IntersectionObserver' in window) {
  const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
      }
    });
  }, observerOptions);

  // Observe all fade-in elements
  document.querySelectorAll('.fade-in').forEach(el => {
    observer.observe(el);
  });
}