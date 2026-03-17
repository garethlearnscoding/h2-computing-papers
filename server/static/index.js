// Warning: This file was made by someone who does NOT know JS
//
// This file was based on https://developer.mozilla.org/en-US/docs/Web/API/HTML_Drag_and_Drop_API/File_drag_and_drop
// and modified with AI 
//
// The website is primarily meant for proof of concept, thus it is not important for this file to be correct

const dropZone = document.getElementById("drop-zone");

dropZone.addEventListener("drop", dropHandler);
window.addEventListener("drop", (e) => {
  if ([...e.dataTransfer.items].some((item) => item.kind === "file")) {
    e.preventDefault();
  }
});
dropZone.addEventListener("dragover", (e) => {
  const fileItems = [...e.dataTransfer.items].filter(
    (item) => item.kind === "file",
  );
  if (fileItems.length > 0) {
    e.preventDefault();
    if (fileItems.some((item) => item.type == 'application/zip')) {
      e.dataTransfer.dropEffect = "copy";
    } else {
      e.dataTransfer.dropEffect = "none";
    }
  }
});

const filenameDisplay = document.getElementById("filename-display");
const fileInput = document.getElementById("file-input");

function dropHandler(ev) {
  ev.preventDefault();
  const files = [...ev.dataTransfer.items]
    .map((item) => item.kind === "file" ? item.getAsFile() : null)
    .filter(Boolean);
  
  if (files.length > 0) {
    const file = files[0];
    const dataTransfer = new DataTransfer();
    dataTransfer.items.add(file);
    fileInput.files = dataTransfer.files;
    displayFilename(file);
  }
}

fileInput.addEventListener("change", (e) => {
  displayFilename(e.target.files[0]);
});

const clearBtn = document.getElementById("clear-btn");
clearBtn.addEventListener("click", () => {
  filenameDisplay.textContent = "";
  const dataTransfer = new DataTransfer();
  fileInput.files = dataTransfer.files;
});

function displayFilename(file) {
  if (file.type == "application/zip") {
    filenameDisplay.textContent = "Selected file: " + file.name;
  }
}

function check_if_file_exists() {
  if (fileInput.files.length === 0) {
    alert("Please attach a zip file first");
    return false;
  }
}
