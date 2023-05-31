// function toggleChat() {
//   var chatInterface = document.getElementById("chat-interface");
//   var chatIcon = document.getElementById("chat-icon");

//   if (chatInterface.style.display === "" || chatInterface.style.display === "none") {
//     chatInterface.style.display = "block";
//     chatIcon.classList.add("active");
//   } else {
//     chatInterface.style.display = "none";
//     chatIcon.classList.remove("active");
//   }
// }

// function createMessageElement(messageText) {
//   var message = document.createElement("div");
//   message.classList.add("chat-message");

//   var messageTextElement = document.createElement("span");
//   messageTextElement.classList.add("message-text");
//   messageTextElement.textContent = messageText;

//   var deleteButton = document.createElement("span");
//   deleteButton.classList.add("delete-button");
//   deleteButton.innerHTML = '<i class="bx bx-trash"></i>';
//   deleteButton.style.display = "none";

//   message.appendChild(messageTextElement);
//   message.appendChild(deleteButton);

//   message.addEventListener("mouseover", function() {
//     deleteButton.style.display = "inline-block";
//   });

//   message.addEventListener("mouseout", function() {
//     deleteButton.style.display = "none";
//   });

//   deleteButton.addEventListener("click", function() {
//     deleteMessage(message);
//   });

//   return message;
// }

// document.getElementById("send-button").addEventListener("click", function() {
//   var chatInput = document.getElementById("chat-input");
//   var messageText = chatInput.value.trim();

//   if (messageText !== "") {
//     var message = createMessageElement(messageText);
//     document.getElementById("chat-box").appendChild(message);
//     chatInput.value = "";
//   }
// });

// function deleteMessage(message) {
//   message.remove();
// }

// document.getElementById("send-button").addEventListener("click", function() {
//   var chatInput = document.getElementById("chat-input");
//   var messageText = chatInput.value.trim();

//   if (messageText !== "") {
//     var message = createMessageElement(messageText);
//     document.getElementById("chat-box").appendChild(message);
//     chatInput.value = "";
//   }
// });

// document.getElementById("chat-box").addEventListener("mouseover", function(e) {
//   if (e.target.classList.contains("chat-message")) {
//     var deleteButton = e.target.querySelector(".delete-button");
//     deleteButton.style.display = "inline-block";
//   }
// });

// document.getElementById("chat-box").addEventListener("mouseout", function(e) {
//   if (e.target.classList.contains("chat-message")) {
//     var deleteButton = e.target.querySelector(".delete-button");
//     deleteButton.style.display = "none";
//   }
// });

// function closeChat() {
//    var chatInterface = document.getElementById("chat-interface");
//    chatInterface.style.display = "none";
//  }

//  const navMenu = document.getElementById('nav-menu');
//  const analyticsDropdown = document.querySelector('.dropdown');
//  const logoutButton = document.getElementById('logout-button');
//  const dropdownMenu = document.getElementById('dropdownMenu');
//  const dropdownItems = dropdownMenu.getElementsByTagName('button');

//  function toggleDropdown() {
//    analyticsDropdown.classList.toggle('active');

//    if (analyticsDropdown.classList.contains('active')) {
//      logoutButton.style.marginTop = '160px';
//    } else {
//      logoutButton.style.marginTop = '0';
//    }
//  }

//  navMenu.addEventListener('click', toggleDropdown);

//  dropdownMenu.addEventListener('click', function(event) {
//    const targetElement = event.target;

//    if (targetElement.tagName === 'BUTTON') {
//      var selectedItem = targetElement.textContent;
//      handleDropdownItemClick(selectedItem);
//    }

//    event.preventDefault();
//    event.stopPropagation();
//  });

//  window.addEventListener('click', function(event) {
//    const targetElement = event.target;
//    if (!targetElement.closest('.dropdown')) {
//      analyticsDropdown.classList.remove('active');
//      logoutButton.style.marginTop = '0';
//    }
//  }); 

function toggleChat() {
  var chatInterface = document.getElementById("chat-interface");
  var chatIcon = document.getElementById("chat-icon");

  if (chatInterface.style.display === "" || chatInterface.style.display === "none") {
    chatInterface.style.display = "block";
    chatIcon.classList.add("active");
  } else {
    chatInterface.style.display = "none";
    chatIcon.classList.remove("active");
  }
}

function createMessageElement(messageText) {
  var message = document.createElement("div");
  message.classList.add("chat-message");

  var messageTextElement = document.createElement("span");
  messageTextElement.classList.add("message-text");
  messageTextElement.textContent = messageText;

  var deleteButton = document.createElement("span");
  deleteButton.classList.add("delete-button");
  deleteButton.innerHTML = '<i class="bx bx-trash"></i>';
  deleteButton.style.display = "none";

  message.appendChild(messageTextElement);
  message.appendChild(deleteButton);

  message.addEventListener("mouseover", function () {
    deleteButton.style.display = "inline-block";
  });

  message.addEventListener("mouseout", function () {
    deleteButton.style.display = "none";
  });

  deleteButton.addEventListener("click", function () {
    deleteMessage(message);
  });

  return message;
}

// document.getElementById("send-button").addEventListener("click", function () {
//   var chatInput = document.getElementById("chat-input");
//   var messageText = chatInput.value.trim();

//   if (messageText !== "") {
//     var message = createMessageElement(messageText);
//     document.getElementById("chat-box").appendChild(message);
//     // chatInput.value = "";
//   }
// });

function deleteMessage(message) {
  message.remove();
}

document.getElementById("chat-box").addEventListener("mouseover", function (e) {
  if (e.target.classList.contains("chat-message")) {
    var deleteButton = e.target.querySelector(".delete-button");
    deleteButton.style.display = "inline-block";
  }
});

document.getElementById("chat-box").addEventListener("mouseout", function (e) {
  if (e.target.classList.contains("chat-message")) {
    var deleteButton = e.target.querySelector(".delete-button");
    deleteButton.style.display = "none";
  }
});

function closeChat() {
  var chatInterface = document.getElementById("chat-interface");
  chatInterface.style.display = "none";
}

const navMenu = document.getElementById('nav-menu');
const analyticsDropdown = document.querySelector('.dropdown');
const logoutButton = document.getElementById('logout-button');
const dropdownMenu = document.getElementById('dropdownMenu');
const dropdownItems = dropdownMenu.getElementsByTagName('input');

function toggleDropdown() {
  analyticsDropdown.classList.toggle('active');

  if (analyticsDropdown.classList.contains('active')) {
    logoutButton.style.marginTop = '160px';
  } else {
    logoutButton.style.marginTop = '0';
  }
}

navMenu.addEventListener('click', toggleDropdown);

dropdownMenu.addEventListener('click', function (event) {
  const targetElement = event.target;

  if (targetElement.tagName === 'INPUT') {
    var selectedItem = targetElement.value;
    handleDropdownItemClick(selectedItem);
    event.stopPropagation(); // Stop the event from propagating to the window
  }
});

// Add this event listener to prevent the dropdown from closing when clicking on the dropdown items
dropdownMenu.addEventListener('mouseup', function (event) {
  event.stopPropagation();
});

function handleDropdownItemClick(selectedItem) {
  // Replace this function with your desired action for the selected item
  console.log(selectedItem);
}

window.addEventListener('click', function (event) {
  const targetElement = event.target;
  if (!targetElement.closest('.dropdown')) {
    analyticsDropdown.classList.remove('active');
    logoutButton.style.marginTop = '0';
  }
});
