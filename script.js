
document.addEventListener('DOMContentLoaded', () => {
  async function fetchAndRenderStations(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = "";

    try {
      const response = await fetch('http://127.0.0.1:5000/radio_stations');
      const stations = await response.json();

      // Convert the stations object to an array for easier iteration
      let stationList = Object.values(stations);

      // Store all stations globally for filtering
      if (containerId === "allStations") {
        window.allStationsData = stationList;
      }

      renderStations(stationList, container);
      renderStations(stationList, container);
    } catch (error) {
      console.error('Error fetching radio stations:', error);
      container.innerHTML = '<p>Could not load radio stations. Please ensure the Flask backend is running.</p>';
    }

  function renderStations(stationsToRender, containerElement) {
    containerElement.innerHTML = ""; // Clear existing stations
    if (stationsToRender.length === 0) {
      containerElement.innerHTML = '<p>No stations found matching your criteria.</p>';
      return;
    }
    for (const station of stationsToRender) {
      const card = document.createElement('div');
      card.className = "station-card";
      // Use station.name as the data-station-id since app.py uses name as key
      card.innerHTML = `
        <img src="${station.logo || 'https://via.placeholder.com/50'}" alt="${station.name}" class="station-logo" />
        <h3 class="station-name">${station.name}</h3>
        <p class="station-genre">${station.genre || 'N/A'}</p>
        <p class="station-country">${station.country || 'N/A'}</p>
        <button class="play-button" data-station-id="${station.name}" data-name="${station.name}" data-logo="${station.logo || 'https://via.placeholder.com/50'}">Play</button>
      `;
      containerElement.appendChild(card);
    }

    containerElement.querySelectorAll("button").forEach(btn => {
      btn.addEventListener("click", async () => {
        const stationId = btn.dataset.stationId;
        const name = btn.dataset.name;
        const logo = btn.dataset.logo;

        try {
          const playResponse = await fetch(`http://127.0.0.1:5000/play_station/${encodeURIComponent(stationId)}`);
          const playData = await playResponse.json();

          if (playResponse.ok) {
            const player = document.querySelector("audio") || new Audio();
            player.src = playData.stream_url;
            player.play();

            document.getElementById("trackTitle").textContent = name;
            document.getElementById("trackArtist").textContent = "Live Radio";
            const art = document.getElementById("albumArt");
            art.innerHTML = `<img src="${logo}" alt="${name}" style="height: 50px; width: 50px; border-radius: 6px;">`;
            document.getElementById("playPause").innerHTML = '<i class="fas fa-pause"></i>';
            document.body.appendChild(player);
          } else {
            alert(playData.error);
          }
        } catch (error) {
          console.error('Error playing station:', error);
          alert('Could not play station. Ensure Flask backend is running and station is playable.');
        }
      });
    });
  }
  }

  fetchAndRenderStations("featuredStations");
  fetchAndRenderStations("allStations");

  // Search functionality
  const searchInput = document.getElementById('searchInput');
  searchInput.addEventListener('input', () => {
    const searchTerm = searchInput.value.toLowerCase();
    const filteredStations = window.allStationsData.filter(station => {
      return (
        station.name.toLowerCase().includes(searchTerm) ||
        (station.genre && station.genre.toLowerCase().includes(searchTerm)) ||
        (station.country && station.country.toLowerCase().includes(searchTerm))
      );
    });
    const allStationsContainer = document.getElementById('allStations');
    renderStations(filteredStations, allStationsContainer);
  });





  // Navigation
  const navLinks = document.querySelectorAll('.nav-link');
  navLinks.forEach(link => {
    link.addEventListener('click', e => {
      e.preventDefault();
      navLinks.forEach(nav => nav.classList.remove('active'));
      link.classList.add('active');
      const section = link.getAttribute('data-section');
      document.querySelectorAll('.content-section').forEach(sec => sec.classList.remove('active'));
      const target = document.getElementById(section + 'Content');
      if (target) target.classList.add('active');
      document.getElementById('pageTitle').textContent = link.textContent.trim();
    });
  });

  // Modal logic
  const profileButton = document.getElementById('profileButton');
  const modal = document.getElementById('registrationModal');
  const closeModal = document.querySelector('.close-modal');
  const form = document.getElementById('registrationForm');
  const countrySelect = document.getElementById('country');
  const countries = ['India', 'USA', 'UK', 'Germany', 'France'];
  countries.forEach(c => {
    const opt = document.createElement('option');
    opt.value = opt.textContent = c;
    countrySelect.appendChild(opt);
  });
  profileButton.onclick = () => modal.classList.add('active');
  closeModal.onclick = () => modal.classList.remove('active');
  modal.onclick = e => { if (e.target === modal) modal.classList.remove('active'); }
  form.onsubmit = e => {
    e.preventDefault();
    alert('Profile Created!');
    modal.classList.remove('active');
    form.reset();
  };
});
