document.addEventListener('DOMContentLoaded', function() {
  const gameItems = document.querySelectorAll('.game-item');

  gameItems.forEach(item => {
    item.addEventListener('click', function() {
      const appid = item.dataset.appid;
      const steamId = item.dataset.steamid;
      console.log(`Fetching achievements for appid: ${appid}, steamId: ${steamId}`); // デバッグログ
      const achievementsDiv = document.getElementById(`achievements-${appid}`);

      // アコーディオンの開閉
      if (achievementsDiv.style.display === 'none' || !achievementsDiv.style.display) {
        achievementsDiv.style.display = 'block';
        achievementsDiv.innerHTML = '<p>IMPORTING...</p>';
        // 実績を取得して表示
        fetch(`/player_data/get_achievements/${steamId}/${appid}/`)
          .then(response => response.json())
          .then(data => {
            console.log("サーバーからのレスポンス:", data); // デバッグログ
            if (data.error) {
              achievementsDiv.innerHTML = '<p>NO INFORMATION</p>';
            } else if (!data.achievements || data.achievements.length === 0) {
              achievementsDiv.innerHTML = '<p>NO ACHIEVEMENTS FOUND</p>';
            } else {
              achievementsDiv.innerHTML = '<ul>' + data.achievements.map(achievement => {
                // achievementから取得
                return `<li>${achievement.apiname || "Unknown"}: ${achievement.name || "Unknown"}</li>`;
              }).join('') + '</ul>';
            }
          })
          .catch(error => {
            achievementsDiv.innerHTML = '<p>NO INFORMATION</p>';
            console.error("Error fetching achievements:", error); 
          });
      } else {
        achievementsDiv.style.display = 'none';
      }
    });
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