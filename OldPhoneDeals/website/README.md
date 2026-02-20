# OldPhoneDeals 

This repository contains a MERN-style phone marketplace app under `website/`:
- `website/frontend`: React + Vite client
- `website/backend`: Express + Mongoose API
- `website/backend/jsondata`: seed JSON files

Other top-level folders:
- `dataset/`: source dataset and default brand images
- `WebApp/`: legacy leftover folder (not part of the running app)

## What The Codebase Does Today

### User-side features
- Browse active listings from MongoDB.
- Search listings by title and filter by brand and max price.
- View "Sold Out Soon" (lowest non-zero stock) and "Best Sellers" (highest average rating with at least 2 reviews).
- Open a listing detail panel with seller name, stock, reviews, and add-to-cart flow.
- Submit reviews (1-5 rating + comment, max 200 chars).
- Toggle review visibility if you are the listing owner or review author.
- Add/remove wishlist items.
- Checkout from cart (stored in `localStorage`) and log purchase events to `SalesLog`.

### Authentication and account management
- User sign-up with password complexity validation.
- Email verification flow before first user sign-in.
- Password reset via emailed token link.
- Profile update (requires password confirmation).
- Password change with email notification.
- Cookie-based JWT session handling (`httpOnly` cookie).

### Seller features
- Create listings from profile (`multipart/form-data` with image upload).
- Enable/disable own listings.
- Delete own listings.
- View comments on own listings.

### Admin features
- Separate admin sign-in endpoint and admin-only view.
- Manage users: view, edit basic fields, enable/disable account, delete.
- Manage listings: edit fields, enable/disable, delete.
- Moderate reviews: hide/show/delete.
- View listing create/delete logs.
- Export sales logs as JSON file (`sales_export.json`).
- Admin action logging in `AdminLog` for key moderation actions.
- Idle auto-logout behavior in frontend for admin sessions (60s inactivity timer).

## Data Layer Notes

- MongoDB database name: `ecommerce-database`.
- On backend startup, if collections are empty:
  - users are seeded from `backend/jsondata/userlist.json`
  - listings are seeded from `backend/jsondata/phonelisting.json`
  - a default admin user is created (`admin@example.com` / password hash for `asd`)
- Current seed files contain:
  - 250 users
  - 112 listings

## Tech Stack

- Frontend: React 19, React Router, Axios, Vite
- Backend: Node.js, Express, Mongoose, JWT, bcrypt, multer, nodemailer
- Database: MongoDB

## Run Locally

1. Install dependencies:
```bash
cd website/frontend
npm install

cd ../backend
npm install
```

2. Create `website/backend/.env` with:
```env
JWT_SECRET=your_jwt_secret
EMAIL_USER=your_gmail_address
EMAIL_PASS=your_gmail_app_password
```

3. Start MongoDB (from `website/`):
```bash
mongod --dbpath=./data/db
```

4. Start backend (new terminal):
```bash
cd website/backend
node app.js
```

5. Start frontend (new terminal):
```bash
cd website/frontend
npm run dev
```

6. Open:
- Frontend: `http://localhost:5173`
- Backend: `http://localhost:3000`

## Current Constraints / Known Gaps

- CORS origin in backend is hardcoded to a specific ngrok URL in `backend/app.js`; local frontend origin may need adjustment.
- Some frontend URLs are hardcoded to `http://localhost:3000`.
- `GET /api/listings/:id` controller currently does not send listing data in its success path.
- Add-listing UI sends a brand value, but backend `createListing` currently stores new listings with brand `"Generic"`.
- No automated test suite is configured in the repository.

