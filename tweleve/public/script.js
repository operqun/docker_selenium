async function loadRegistrations() {
  const res = await fetch("/api/registrations");
  const data = await res.json();
  const tbody = document.querySelector("#regTable tbody");
  tbody.innerHTML = "";
  data.forEach(r => {
    tbody.innerHTML += `<tr><td>${r.id}</td><td>${r.name}</td><td>${r.event}</td></tr>`;
  });
  document.getElementById("count").textContent = data.length;
}

async function loadHost() {
  const res = await fetch("/health");
  const data = await res.json();
  document.getElementById("host").textContent = data.host;
}

document.getElementById("regForm").addEventListener("submit", async function (e) {
  e.preventDefault();
  const name    = document.getElementById("name").value.trim();
  const email   = document.getElementById("email").value.trim();
  const phone   = document.getElementById("phone").value.trim();
  const college = document.getElementById("college").value.trim();
  const event   = document.getElementById("event").value;
  const error   = document.getElementById("error");
  const success = document.getElementById("success");
  error.textContent = "";
  success.textContent = "";

  if (!name || !college) { error.textContent = "Name and College are required."; return; }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) { error.textContent = "Please enter a valid email address."; return; }
  if (!/^[6-9][0-9]{9}$/.test(phone)) { error.textContent = "Mobile number must be 10 digits starting with 6-9."; return; }
  if (!event) { error.textContent = "Please select an event."; return; }

  const res = await fetch("/api/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, email, phone, college, event })
  });
  const data = await res.json();
  if (res.ok) {
    success.textContent = data.message;
    this.reset();
    loadRegistrations();
  } else {
    error.textContent = data.error;
  }
});

loadRegistrations();
loadHost();