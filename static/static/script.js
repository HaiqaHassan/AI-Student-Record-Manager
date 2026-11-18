
const form = document.getElementById("student-form");
const notice = document.getElementById("notice");
const recordsBody = document.getElementById("records-body");
const aiResult = document.getElementById("ai-result");
let allStudents = [];
let selectedId = null;

function showNotice(message, type = "success") {
  notice.textContent = message;
  notice.className = `notice ${type}`;
  window.scrollTo({ top: 0, behavior: "smooth" });
  setTimeout(() => notice.classList.add("hidden"), 4500);
}

function parseForm() {
  const subjects = document.getElementById("subjects").value.split(",").map(x => x.trim());
  const marks = document.getElementById("marks").value.split(",").map(x => x.trim());
  if (subjects.length !== marks.length) throw new Error("Enter the same number of subjects and marks.");
  return {
    id: document.getElementById("student-id").value.trim(),
    name: document.getElementById("student-name").value.trim(),
    class: document.getElementById("student-class").value.trim(),
    subjects,
    marks
  };
}

async function api(url, options = {}) {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "Something went wrong.");
  return data;
}

function escapeHTML(value) {
  return String(value).replace(/[&<>"']/g, char => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;"
  }[char]));
}

function renderStudents(records) {
  if (!records.length) {
    recordsBody.innerHTML = '<tr><td colspan="7" class="empty">No student records found.</td></tr>';
    return;
  }
  recordsBody.innerHTML = records.map(student => {
    const subjects = Object.entries(student.marks).map(([name, mark]) =>
      `${escapeHTML(name)}: ${Number(mark).toFixed(Number(mark) % 1 ? 2 : 0)}`
    ).join("<br>");
    return `<tr data-id="${escapeHTML(student.id)}" class="${selectedId === student.id ? "selected" : ""}">
      <td>${escapeHTML(student.id)}</td><td>${escapeHTML(student.name)}</td>
      <td>${escapeHTML(student.class)}</td><td>${subjects}</td>
      <td>${student.total}</td><td>${student.average}%</td><td><span class="grade">${escapeHTML(student.grade)}</span></td>
    </tr>`;
  }).join("");
}

async function loadStudents(records = null) {
  allStudents = await api("/api/students");
  renderStudents(records || allStudents);
}

function selectStudent(student) {
  selectedId = student.id;
  document.getElementById("student-id").value = student.id;
  document.getElementById("student-id").readOnly = true;
  document.getElementById("student-name").value = student.name;
  document.getElementById("student-class").value = student.class;
  document.getElementById("subjects").value = Object.keys(student.marks).join(", ");
  document.getElementById("marks").value = Object.values(student.marks).join(", ");
  renderStudents(allStudents);
}

function clearForm() {
  form.reset();
  selectedId = null;
  document.getElementById("student-id").readOnly = false;
  renderStudents(allStudents);
  aiResult.textContent = "Your personalized AI feedback will appear here.";
}

form.addEventListener("submit", async event => {
  event.preventDefault();
  try {
    const result = await api("/api/students", { method: "POST", body: JSON.stringify(parseForm()) });
    showNotice(result.message);
    clearForm();
    await loadStudents();
  } catch (error) { showNotice(error.message, "error"); }
});

document.getElementById("update-btn").addEventListener("click", async () => {
  if (!selectedId) return showNotice("Select a student row before updating.", "error");
  try {
    const data = parseForm();
    const result = await api(`/api/students/${encodeURIComponent(selectedId)}`, {
      method: "PUT", body: JSON.stringify(data)
    });
    showNotice(result.message);
    clearForm();
    await loadStudents();
  } catch (error) { showNotice(error.message, "error"); }
});

document.getElementById("delete-btn").addEventListener("click", async () => {
  if (!selectedId) return showNotice("Select a student row before deleting.", "error");
  const student = allStudents.find(item => item.id === selectedId);
  if (!window.confirm(`Delete the record for ${student.name} (${student.id})?`)) return;
  try {
    const result = await api(`/api/students/${encodeURIComponent(selectedId)}`, { method: "DELETE" });
    showNotice(result.message);
    clearForm();
    await loadStudents();
  } catch (error) { showNotice(error.message, "error"); }
});

recordsBody.addEventListener("click", event => {
  const row = event.target.closest("tr[data-id]");
  if (!row) return;
  const student = allStudents.find(item => item.id === row.dataset.id);
  if (student) selectStudent(student);
});

document.getElementById("clear-btn").addEventListener("click", clearForm);
document.getElementById("show-all-btn").addEventListener("click", () => {
  document.getElementById("search-input").value = "";
  renderStudents(allStudents);
});
document.getElementById("search-btn").addEventListener("click", () => {
  const query = document.getElementById("search-input").value.trim().toLowerCase();
  renderStudents(allStudents.filter(student =>
    student.id.toLowerCase().includes(query) || student.name.toLowerCase().includes(query)
  ));
});
document.getElementById("search-input").addEventListener("keydown", event => {
  if (event.key === "Enter") document.getElementById("search-btn").click();
});

async function runAI(kind) {
  if (!selectedId) return showNotice("Select a student row before using an AI feature.", "error");
  aiResult.textContent = kind === "analyze" ? "Analyzing academic performance… Please wait." : "Creating personalized study tips… Please wait.";
  try {
    const data = await api(`/api/ai/${kind}/${encodeURIComponent(selectedId)}`, { method: "POST", body: "{}" });
    aiResult.textContent = data.result;
  } catch (error) {
    aiResult.textContent = error.message;
  }
}
document.getElementById("analyze-btn").addEventListener("click", () => runAI("analyze"));
document.getElementById("tips-btn").addEventListener("click", () => runAI("tips"));

loadStudents().catch(error => showNotice(error.message, "error"));
