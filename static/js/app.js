const grammarForm = document.getElementById('grammar-form');
var containerResultField = document.querySelector(".container-result-field");
const loader = document.querySelector(".loader");
var grammarButton = document.querySelector(".grammar-button");
grammarForm.addEventListener('submit', (event) => {
  event.preventDefault();
    loader.style.display = "inline-block";
    grammarButton.style.display="none";
  const formData = new FormData(grammarForm);
  console.log(formData)
  fetch('/grammar-check-post', {
    method: 'POST',
    body: formData
  })
  .then(response => response.text())
  .then(data => {
    loader.style.display = "none";
    grammarButton.style.display="block";
    containerResultField.style.display = "block";
    let divcorrect = document.querySelector(".corrected_text")
    divcorrect.innerText = data;
  })
  .catch(error => console.error(error));
});




