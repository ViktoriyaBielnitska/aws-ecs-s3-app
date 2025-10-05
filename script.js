const form = document.getElementById("addForm");
const input = document.getElementById("content");
const list = document.getElementById("entries");

const API_URL = "https://api.nginxawsapp.icu/api/entries";

async function loadEntries() {
  try {
    list.innerHTML = "<li>Loading...</li>";
    const res = await fetch(API_URL);
    if (!res.ok) throw new Error(`Server error: ${res.status}`);
    const data = await res.json();

    list.innerHTML = "";
    data.forEach(e => {
      const li = document.createElement("li");
      li.textContent = e.content;

      const delBtn = document.createElement("button");
      delBtn.textContent = "Delete";
      delBtn.style.marginLeft = "10px";
      delBtn.onclick = async () => {
        try {
          await fetch(`${API_URL}/${e.id}`, { method: "DELETE" });
          loadEntries();
        } catch (err) {
          console.error("Error deleting entry:", err);
        }
      };

      li.appendChild(delBtn);
      list.appendChild(li);
    });
  } catch (err) {
    console.error("Error loading entries:", err);
    list.innerHTML = "<li style='color:red'>Failed to load entries</li>";
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const text = input.value.trim();
  if (!text) return;

  try {
    await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content: text })
    });
    input.value = "";
    loadEntries();
  } catch (err) {
    console.error("Error adding entry:", err);
  }
});

loadEntries();
