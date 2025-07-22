<br />
<div align="center">
    <img src="frontend/public/nokia.png" alt="Logo" width="60">
    <h3 align="center">OldPhoneDeals</h3>
    
        
    </p>
</div>

<br />

**_OldPhoneDeals_** is an eCommerce web application developed for COMP4347 Web Application Development. Built using the MERN stack (MongoDB, Express, React, Node.js), this project showcases a complete three-tier architecture supporting both user and admin functionality. The platform allows users to browse, search, filter, and purchase secondhand phones, as well as manage their listings and reviews. It also implements essential features such as user authentication, email verification, wishlist management, and a checkout process.

<center>
  <img src="frontend/public/home.png" width="512">
  <p><em>Homepage of OldPhoneDeals</em></p>
</center>

A dedicated admin interface enables site administrators to manage users, listings, and reviews, monitor sales and activity logs, and enforce platform policies. The application adheres to SPA principles, follows the MVC design pattern, and integrates robust security practices including password hashing and session handling. All interactions are handled asynchronously to ensure a responsive user experience, and the system is designed to scale dynamically beyond the provided dataset.

<br>

![MongoDB](https://img.shields.io/badge/MongoDB-4EA94B?style=for-the-badge&logo=mongodb&logoColor=white)
![Express.js](https://img.shields.io/badge/Express%20js-000000?style=for-the-badge&logo=express&logoColor=white)
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![Node.js](https://img.shields.io/badge/Node%20js-339933?style=for-the-badge&logo=nodedotjs&logoColor=white)


# Getting started

## Install dependencies

**1. Clone this repository and navigate to it in your terminal.**

   ```bash
   cd TUT15-G1-A2/
   ```

**2. Install dependencies for both backend and frontend scripts.**
   ```bash
   cd frontend
   npm install

   cd ../backend
   npm install
   ```

**3. Ensure MongoDB Tools are installed**

   Make sure the following are already installed on your machine:
   - MongoDB Server
   - mongosh
   - MongoDB Database Tools (for `mongoimport`)

   Add MongoDB to System Path (Windows):
   1. Search for **Environment Variables** in Windows.
   2. Under **System Variables**, find and select `Path`, then click **Edit**.
   3. Click **New** and add the paths for:
      - Example path: `C:\Program Files\MongoDB\Server\8.0\bin`
      - Get the path by right clicking the bin folder of installed extensions and clicking `Copy Path` for:
         - MongoDB Server 
         - MongoDB Shell
         - MongoDB Tools
   4. Restart **CMD** to apply changes.
   5. If you have completed the above processes correctly, then you can see the results of:
   ```bash
   mongod --version
   mongosh --version
   mongoimport --version
   ```

## Setup the MongoDB Database

1. Create the database directory in the backend directory
   ```bash
   # Windows
   md data\db

   # Unix
   mkdir -p data/db
   ```

2. Start the MongoDB server
   ```bash
   # Windows
   mongod --dbpath=.\data\db

   # Unix
   mongod --dbpath=data/db
   ```

Leave this terminal (Terminal 1) running. This is your local MongoDB server.

## Run the Project

1. Place your JSON data in the `backend/jsondata` directory. This should be two separate files: `phonelisting.json` for listing information and `userlist.json` for user information.

2. Ensure you have the populated `.env` file placed in the `backend` folder. It contains important private keys required for user management.

3. In a **new terminal** (Terminal 2), run:
   ```bash
   cd backend
   node app.js
   ```

4. In a **new terminal** (Terminal 3), run:
   ```bash
   cd frontend
   npm run dev
   ```

You should now be able to view the project at ``localhost:5173``.

## Debugging notes 

If have a user login or listings related error such as having users or listings before populating the database, make sure to go to the database. 

If you have users already and you run the backend, you will be never be able to login as admin as admin is added once you run an empty userlist on the backend.

```bash
use ecommerce-database

db.users.drop()
db.listings.drop()
```

Re-run the backend node app.js in your backend terminal and it will repopulate the database with the users and listings again.

This means that you have to sign up again and follow the steps to log in once more.

### The admin credentials
   ```bash
   firstname: 'Admin',
   lastname: 'User',
   email: 'admin@example.com',
   password: 'asd'
   ```

### Sign up and sign in.

When signing up make sure you use a valid GMAIL account that you can log into and verify.
All new passwords should also be a minimum of 8 characters with 1 Capital letter, number and symbol.

For the email verification step, make sure to check your SPAM folders and click the link to verify your email and log in again to go inside the web app.

### .env

This submission contains a .env file with the following content 

JWT_SECRET=r82gh!@94jHG!@fklgshga@Yp*r723hfhs98d
EMAIL_USER=axtoncahyadi@gmail.com
EMAIL_PASS=bcww lcxs whni xfsd
EMAIL_FROM=axtoncahyadi@gmail.com

