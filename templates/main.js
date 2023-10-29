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

function uploadFile() {
  const fileInput = document.getElementById('fileInput');
  if (fileInput.files.length === 0) {
    alert('Please select a file first!');
    return;
  }

  const formData = new FormData();
  formData.append('file', fileInput.files[0]);

  fetch('/server_endpoint', {  // replace '/server_endpoint' with server's endpoint
    method: 'POST',
    body: formData
  })
    .then(response => response.json())
    .then(data => {
      alert('File uploaded successfully!');
      // you can handle server's response here if needed
    })
    .catch(error => {
      alert('Error uploading file: ' + error.message);
    });
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
