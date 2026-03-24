// Generate bubbles dynamically
const container = document.querySelector(".bubble-container");

for (let i = 0; i < 15; i++) {
  const bubble = document.createElement("div");
  bubble.classList.add("bubble");
  
  // Random size
  const size = Math.random() * 12 + 8;
  bubble.style.width = `${size}px`;
  bubble.style.height = `${size}px`;
  
  // Random horizontal position
  bubble.style.left = `${Math.random() * 100}%`;
  
  // Random animation duration
  bubble.style.animationDuration = `${4 + Math.random() * 3}s`;
  
  container.appendChild(bubble);
}


// suji popup





// Get the modal
var modal = document.getElementById("imageModal");

// Get the image and insert it inside the modal
var modalImg = document.getElementById("img01");

function openModal(imageSrc) {
  modal.style.display = "block";
  modalImg.src = imageSrc;
}

// Get the <span> element that closes the modal
var span = document.getElementsByClassName("close-btn")[0];

// When the user clicks on <span> (x), close the modal
span.onclick = function() { 
  modal.style.display = "none";
}

// When the user clicks anywhere outside of the image, close it
window.onclick = function(event) {
  if (event.target == modal) {
    modal.style.display = "none";
  }
}