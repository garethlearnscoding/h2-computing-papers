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
      console.log(fileItems.at(0).type)
      e.dataTransfer.dropEffect = "none";
    }
  }
});

const filename = document.getElementById("filename");
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
    displayImages(file);
  }
}

fileInput.addEventListener("change", (e) => {
  displayImages(e.target.files[0]);
});

const clearBtn = document.getElementById("clear-btn");
clearBtn.addEventListener("click", () => {
  filename.textContent = "";
  const dataTransfer = new DataTransfer();
  fileInput.files = dataTransfer.files;
});

function displayImages(file) {
  if (file.type == "application/zip") {
    filename.textContent = "Selected file: " + file.name;
  }
}

function check_if_file_exists() {
  if (fileInput.files.length === 0) {
    alert("Please upload a file");
    return false;
  }
}
