// ----------------------------------------------------------------------------------------
//-------------------------------- Calendar widget ----------------------------------------
// ----------------------------------------------------------------------------------------

const ticketContainer = document.querySelector('.ticket-container');

const currentTimePicker = flatpickr("#current-time", {
  enableTime: true,
  dateFormat: "Y-m-d H:i",
  time_24hr: true,
  appendTo: ticketContainer,
});

const deprtureTimePicker = flatpickr("#departure-time", {
  enableTime: true,
  dateFormat: "Y-m-d H:i",
  time_24hr: true,
  appendTo: ticketContainer,
});

const arrivalTimePicker = flatpickr("#arrival-time", {
  enableTime: true,
  dateFormat: "Y-m-d H:i",
  time_24hr: true,
  appendTo: ticketContainer,
});


// ----------------------------------------------------------------------------------------
//-------------------------------- Post prediction ----------------------------------------
// ----------------------------------------------------------------------------------------


document.getElementById("predict-btn").addEventListener("click", () => {
  const startTimestamp = currentTimePicker.selectedDates[0]?.toISOString();
  const srcArrivalPlan = deprtureTimePicker.selectedDates[0]?.toISOString();
  const dstArrivalPlan = arrivalTimePicker.selectedDates[0]?.toISOString();

  const data = {
    start_timestamp: startTimestamp,
    src_station: document.querySelector(".station-input").value,
    dst_station: document.querySelector(".destination-input").value,
    line: document.querySelector(".line-input").value,
    src_arrival_plan: srcArrivalPlan,
    src_arrival_delay: parseInt(document.querySelector(".delay-input").value) || 0,
    dst_arrival_plan: dstArrivalPlan,
    info: document.querySelector(".info-input").value || ""
  };

  // POST to backend
  fetch("http://localhost:5530/predict", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  })
    .then(res => res.json())  
    .then(response => {
        const newTicket = document.createElement("div");
        newTicket.classList.add("ticket-container","prediction-ticket");

        // Build probability lines dynamically
      const probLines = `
        <p>5 minutes late: ${Math.round(response.dst_arrival_delay_over_5_minutes_prob * 100)}%</p>
        <p>10 minutes late: ${Math.round(response.dst_arrival_delay_over_10_minutes_prob * 100)}%</p>
        <p>15 minutes late: ${Math.round(response.dst_arrival_delay_over_15_minutes_prob * 100)}%</p>
        <p>20 minutes late: ${Math.round(response.dst_arrival_delay_over_20_minutes_prob * 100)}%</p>
        <p>25 minutes late: ${Math.round(response.dst_arrival_delay_over_25_minutes_prob * 100)}%</p>
        <p>30 minutes late: ${Math.round(response.dst_arrival_delay_over_30_minutes_prob * 100)}%</p>
      `;

      newTicket.innerHTML = `
        <div class="prediction-section">
          <img src="ticket_clear.svg" alt="train">
          
          <div class="prediction-text">
              <p>Possibilities that the train is over:</p>

              <div class="probabilities">
                  ${probLines}
              </div>
          </div>
        </div>
      `;


        document
            .querySelector(".ticket-container:last-of-type")
            .after(newTicket);
    })
    //.catch(err => console.error(err));
});



// ----------------------------------------------------------------------------------------
//--------------------------------------- Reset -------------------------------------------
// ----------------------------------------------------------------------------------------



document.querySelector(".reset-btn").addEventListener("click", () => {
    const inputs = document.querySelectorAll("input");
    inputs.forEach(input => input.value = "");

    const predictionDivs = document.querySelectorAll(".prediction-ticket");
    predictionDivs.forEach(div => div.remove());

    currentTimePicker.clear();
    deprtureTimePicker.clear();
    arrivalTimePicker.clear();

});



// ----------------------------------------------------------------------------------------
//--------------------------------- dropdowns ---------------------------------------------
// ----------------------------------------------------------------------------------------



function setupAutocomplete(inputId, suggestionContainerId, apiEndpoint, extractName = false) {
    const input = document.getElementById(inputId);
    const container = document.getElementById(suggestionContainerId);
    let options = [];

    // Fetch options from API
    fetch(apiEndpoint)
      .then(res => res.json())
      .then(data => {
          // If extractName=true, map to only the 'name' property
          options = extractName ? data.map(item => item.name) : data;
      })
      .catch(err => console.error(`Failed to load options from ${apiEndpoint}:`, err));

    input.addEventListener("input", () => {
        const value = input.value.toLowerCase();
        container.innerHTML = "";

        if (!value) {
            container.style.display = "none";
            return;
        }

        const filtered = options.filter(opt => opt.toLowerCase().includes(value));

        filtered.forEach(opt => {
            const div = document.createElement("div");
            div.textContent = opt;
            div.addEventListener("click", () => {
                input.value = opt;
                container.style.display = "none";
            });
            container.appendChild(div);
        });

        container.style.display = filtered.length ? "block" : "none";
    });

    // Hide suggestions when clicking outside
    document.addEventListener("click", e => {
        if (!container.contains(e.target) && e.target !== input) {
            container.style.display = "none";
        }
    });
}


// Initialize all autocompletes
setupAutocomplete("src-station", "src-station-suggestions", "http://localhost:5530/stations", true);
setupAutocomplete("dst-station", "dst-station-suggestions", "http://localhost:5530/stations", true);
setupAutocomplete("line", "line-suggestions", "http://localhost:5530/lines");
setupAutocomplete("info", "info-suggestions", "http://localhost:5530/info-options");

