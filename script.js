window.addEventListener('resize', function() {
    var navbarHeight = document.getElementById('navbar').offsetHeight;
    document.getElementById('custom-iframe').style.height = `calc(100vh - ${navbarHeight}px)`;
  });
  