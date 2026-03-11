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

window.addEventListener("dragover", (e) => {
  const fileItems = [...e.dataTransfer.items].filter(
    (item) => item.kind === "file",
  );
  if (fileItems.length > 0) {
    e.preventDefault();
    if (!dropZone.contains(e.target)) {
      e.dataTransfer.dropEffect = "none";
    }
  }
});
const filename = document.getElementById("filename")

function displayImages(files) {
  for (const file of files) {
    if (file.type == "application/zip") {
      filename.textContent = "Selected file: " + file.name;
    }
  }
}

function dropHandler(ev) {
  ev.preventDefault();
  const files = [...ev.dataTransfer.items]
    .map((item) => item.getAsFile())
    .filter((file) => file);
  displayImages(files);
  console.log(fileInput.nodeValue);
}

const fileInput = document.getElementById("file-input");
fileInput.addEventListener("change", (e) => {
  displayImages(e.target.files);
});

const clearBtn = document.getElementById("clear-btn");
clearBtn.addEventListener("click", () => {
  // for (const img of preview.querySelectorAll("img")) {
  //   URL.revokeObjectURL(img.src);
  // }
  filename.textContent = "";
  fileInput.value = null
});

function check_if_file_exists() {
  if (fileInput.value == "") {
    alert("Please upload a file");
    return false
  }
}
