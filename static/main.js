function dragOverHandler(event) {
  event.preventDefault();
  document.querySelector('.file-upload-wrapper').classList.add('drag-over');
}

function dragLeaveHandler(event) {
  document.querySelector('.file-upload-wrapper').classList.remove('drag-over');
}

function dropHandler(event) {
  event.preventDefault();
  document.querySelector('.file-upload-wrapper').classList.remove('drag-over');
  const fileInput = document.getElementById('fileInput');
  fileInput.files = event.dataTransfer.files;
  showFileName();
}

function showFileName() {
  const fileInput = document.getElementById('fileInput');
  const fileNameDisplay = document.getElementById('selectedFileName');
  const uploadBtn = document.getElementById('uploadBtn');
  if (fileInput.files.length > 0) {
    fileNameDisplay.textContent = ' ' + fileInput.files[0].name;
    uploadBtn.style.display = 'block';  // show the "Upload" button
  } else {
    fileNameDisplay.textContent = '';
    uploadBtn.style.display = 'none';  // hide the "Upload" button
  }
}

function showLoading() {
  document.getElementById('loadingOverlay').style.display = 'flex';
}
