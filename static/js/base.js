const currentPath = window.location.pathname;
document.querySelectorAll('.nav-link').forEach(function(link) {
  if (link.getAttribute('href') === currentPath) {
    link.classList.add('active');
  }
});
