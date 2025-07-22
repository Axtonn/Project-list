import { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import axios from 'axios';

function VerifyEmail() {
  const [searchParams] = useSearchParams();
  const [status, setStatus] = useState('verifying');
  const navigate = useNavigate();

  useEffect(() => {
    const verifyToken = async () => {
      const token = searchParams.get('token');
      if (!token) {
        setStatus('invalid');
        return;
      }

      try {
        const res = await axios.get(`http://localhost:3000/api/verify-email?token=${token}`);
        if (res.data.success) {
          setStatus('success');
          setTimeout(() => navigate('/auth'), 1000); // Redirect after 3 seconds
        } else {
          setStatus('failed');
        }
      } catch (err) {
        setStatus('failed');
      }
    };

    verifyToken();
  }, [searchParams, navigate]);

  return (
    <div className="verify-container" style={{ padding: '2rem', textAlign: 'center' }}>
      {status === 'verifying' && <p>Verifying your email...</p>}
      {status === 'success' && <p>Email verified successfully! Redirecting to login...</p>}
      {status === 'failed' && <p>Verification failed or link expired. Please try again.</p>}
      {status === 'invalid' && <p>Invalid verification link.</p>}
    </div>
  );
}

export default VerifyEmail;
