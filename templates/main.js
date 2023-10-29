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
