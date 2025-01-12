document.addEventListener('DOMContentLoaded', function() {
  // フェードイン効果を実行
  const fadeInElements = document.querySelectorAll('.fade-in');
  fadeInElements.forEach(element => {
    element.style.opacity = 1;
  });

  particlesJS("particles-js", {
    particles: {
      number: { value: 80, density: { enable: true, value_area: 800 } },
      color: { value: ['#FFB6C1', '#F8C8D1', '#F9E1F4', 'F5A8D1'] }, // パーティクルの色
      shape: {
        type: "star",
        stroke: { width: 0, color: "#000000" },
      },
      opacity: {
        value: 0.3,
        random: true,
        anim: { enable: false, speed: 1, opacity_min: 0.1, sync: false },
      },
      size: {
        value: 4,
        random: true,
        anim: { enable: false, speed: 40, size_min: 0.1, sync: false },
      },
      line_linked: {
        enable: true,
        distance: 150,
        color: "#FFD700",
        opacity: 0.2,
        width: 1,
      },
      move: {
        enable: true,
        speed: 6,
        direction: "none",
        random: false,
        straight: false,
        out_mode: "out",
        attract: { enable: false, rotateX: 600, rotateY: 1200 },
      },
    },
    interactivity: {
      detect_on: "canvas",
      events: {
        onhover: { enable: true, mode: "repulse" },
        onclick: { enable: true, mode: "push" },
        resize: true,
      },
      modes: {
        repulse: { distance: 100, duration: 0.4 },
      },
    },
    retina_detect: true,
  });
});