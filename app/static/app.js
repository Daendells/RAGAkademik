const form = document.getElementById("ask-form");
const input = document.getElementById("question");
const button = document.getElementById("ask-button");
const result = document.getElementById("result");
const statusEl = document.getElementById("status");
const answerEl = document.getElementById("answer");
const sourcesEl = document.getElementById("sources");

function setStatus(text, isError = false) {
  statusEl.textContent = text;
  statusEl.classList.toggle("error", isError);
}

// Model text is inserted with textContent only; citations become buttons that open their source.
function renderAnswer(text, sources) {
  answerEl.replaceChildren();
  for (const part of text.split(/(\[\d+\])/)) {
    const m = part.match(/^\[(\d+)\]$/);
    if (m && sources[Number(m[1]) - 1]) {
      const n = Number(m[1]);
      const cite = document.createElement("button");
      cite.type = "button";
      cite.className = "cite";
      cite.textContent = n;
      cite.setAttribute("aria-label", `Buka sumber ${n}: ${sources[n - 1].citation}`);
      cite.addEventListener("click", () => openSource(n));
      answerEl.append(cite);
    } else {
      // Only **bold** is rendered; everything else stays plain text.
      part.split(/\*\*(.+?)\*\*/g).forEach((piece, i) => {
        if (i % 2) {
          const strong = document.createElement("strong");
          strong.textContent = piece;
          answerEl.append(strong);
        } else {
          answerEl.append(piece);
        }
      });
    }
  }
}

function renderSources(sources) {
  sourcesEl.replaceChildren();
  if (!sources.length) return;
  const title = document.createElement("h2");
  title.textContent = "Sumber";
  sourcesEl.append(title);
  sources.forEach((s, i) => {
    const item = document.createElement("details");
    item.className = "source";
    item.id = `source-${i + 1}`;
    const summary = document.createElement("summary");
    summary.textContent = `[${i + 1}] ${s.citation}`;
    const body = document.createElement("pre");
    body.textContent = s.text;
    item.append(summary, body);
    sourcesEl.append(item);
  });
}

function openSource(n) {
  const item = document.getElementById(`source-${n}`);
  if (!item) return;
  item.open = true;
  item.scrollIntoView({ behavior: "smooth", block: "nearest" });
  item.classList.add("flash");
  setTimeout(() => item.classList.remove("flash"), 900);
}

async function ask(question) {
  result.hidden = false;
  answerEl.replaceChildren();
  sourcesEl.replaceChildren();
  setStatus("Mencari pasal yang relevan…");
  button.disabled = true;

  let streamed = "";
  try {
    const response = await fetch("/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
    if (!response.ok) {
      setStatus("Pertanyaan belum bisa diproses. Tulis pertanyaan 1–500 karakter.", true);
      return;
    }
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    for (;;) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop();
      for (const line of lines) {
        if (!line.startsWith("data: ")) continue;
        const event = JSON.parse(line.slice(6));
        if (event.type === "token") {
          setStatus("Menyusun jawaban…");
          streamed += event.text;
          answerEl.textContent = streamed.replace(/\[C\d+\]/g, "").replace(/\*\*/g, "");
        } else if (event.type === "sources") {
          renderAnswer(event.answer, event.sources);
          renderSources(event.sources);
          setStatus(event.refused ? "" : event.cited ? "" : "Jawaban ini tidak menyebut pasal. Cek sumber di bawah.");
        } else if (event.type === "error") {
          setStatus(event.message, true);
        }
      }
    }
  } catch {
    setStatus("Koneksi terputus. Coba lagi beberapa saat lagi.", true);
  } finally {
    button.disabled = false;
  }
}

form.addEventListener("submit", (e) => {
  e.preventDefault();
  const question = input.value.trim();
  if (question) ask(question);
});

input.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    form.requestSubmit();
  }
});

document.querySelectorAll(".example").forEach((b) =>
  b.addEventListener("click", () => {
    input.value = b.textContent;
    form.requestSubmit();
  })
);
