const backendUrlInput = document.getElementById("backendUrl");
const pdfFileInput = document.getElementById("pdfFile");
const uploadBtn = document.getElementById("uploadBtn");
const statusDiv = document.getElementById("status");
const questionInput = document.getElementById("questionInput");
const askBtn = document.getElementById("askBtn");
const answerBox = document.getElementById("answerBox");

let sessionId = null;

uploadBtn.addEventListener("click", async () => {
  const file = pdfFileInput.files[0];
  if (!file) {
    alert("Please select a PDF first.");
    return;
  }

  const backendUrl = backendUrlInput.value.replace(/\/$/, "");
  const formData = new FormData();
  formData.append("file", file);

  statusDiv.textContent = "Uploading and processing PDF...";
  answerBox.textContent = "";

  try {
    const res = await fetch(backendUrl + "/upload", {
      method: "POST",
      body: formData,
    });
    const data = await res.json();
    sessionId = data.session_id;
    statusDiv.textContent = "PDF uploaded. Session ID: " + sessionId;
  } catch (err) {
    console.error(err);
    statusDiv.textContent = "Upload failed. Check console.";
  }
});

askBtn.addEventListener("click", async () => {
  if (!sessionId) {
    alert("Upload a PDF first.");
    return;
  }
  const question = questionInput.value.trim();
  if (!question) return;

  const backendUrl = backendUrlInput.value.replace(/\/$/, "");
  answerBox.textContent = "Thinking...";

  try {
    const res = await fetch(backendUrl + "/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId, question }),
    });
    const data = await res.json();
    answerBox.textContent = data.answer;
  } catch (err) {
    console.error(err);
    answerBox.textContent = "Error calling backend. Check console.";
  }
});
