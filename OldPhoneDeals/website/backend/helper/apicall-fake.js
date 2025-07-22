// begin by starting the server
// node app.js 
// on a separate terminal run
// node apicall-fake.js
// this will send a fake login to app.js

// Fake login call
/*
fetch("http://localhost:3000/api/submit", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
      inputValue: "email",
  })
})
.then(res => res.json())
.then(data => console.log("Login response:", data))
.catch(err => console.error("Login error:", err));
*/
fetch("http://localhost:3000/api/sign-in", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    username: "email",
    password: "password123"
  })
})
.then(res => res.json())
.then(data => console.log("Login response:", data))
.catch(err => console.error("Login error:", err));


// Fake sign-up call
/*
fetch("http://localhost:3000/api/sign-up", {
  method: "POST",
  headers: {
    "Content-Type": "application/json"
  },
  body: JSON.stringify({
    inputFirstName: "Alicea",
    inputLastName: "Smith",
    inputEmail: "alice@example.com",
    inputPassword: "password123"
  })
})
.then(res => res.json())
.then(data => console.log("Login response:", data))
.catch(err => console.error("Login error:", err));
*/
