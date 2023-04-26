const grammarForm = document.getElementById('grammar-form');
grammarForm.addEventListener('submit', (event) => {
  event.preventDefault();
  const formData = new FormData(grammarForm);
  console.log(formData)
  fetch('/grammar-check-post', {
    method: 'POST',
    body: formData
  })
  .then(response => response.text())
  .then(data => {
    let divcorrect = document.querySelector(".corrected_text")
    divcorrect.innerText = data;
  })
  .catch(error => console.error(error));
});

