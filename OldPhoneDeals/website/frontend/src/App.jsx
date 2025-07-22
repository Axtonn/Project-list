import './App.css'
import { Routes, Route } from 'react-router-dom';
import Checkout from './Checkout';
import Auth from './pages/Auth'
import Home from './Home';
import Profile from './pages/Profile';
import AddListing from './pages/AddListing';
import AdminAuth from './pages/AdminAuth'
import AdminView from './pages/AdminView';
import ResetRequest from './pages/ResetRequest';
import ResetForm from './pages/ResetForm';
import RequireRole from './components/RequireRole';
import Wishlist from './pages/Wishlist';
import VerifyEmail from './pages/VerifyEmail';
import useIdleLogout from './utils/useIdleLogout';

function App() {
  useIdleLogout();
  return (
    <>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/checkout" element={<RequireRole><Checkout /></RequireRole>} />
        <Route path="/profile" element={<RequireRole><Profile /></RequireRole>} />
        <Route path="/add-listing" element={<RequireRole><AddListing /></RequireRole>} />
        <Route path="/wishlist" element={<RequireRole><Wishlist /></RequireRole>} />
        <Route path="/auth" element={<Auth/>} />
        <Route path="/admin" element={<AdminAuth/>} />
        <Route path="/admin-view" element={<RequireRole role="admin"><AdminView /></RequireRole>} />
        <Route path="/reset-password" element={<ResetRequest />} />
        <Route path="/reset-password-form" element={<ResetForm />} />
        <Route path="/verify-email" element={<VerifyEmail />} />
      </Routes>
    </>
  )
}

export default App
