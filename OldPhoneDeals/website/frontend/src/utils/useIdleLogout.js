import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

// timeout function for admin, set to a minute
const useIdleLogout = (timeoutMs = 60 * 1000) => {
  const navigate = useNavigate();
  const [secondsLeft, setSecondsLeft] = useState(timeoutMs / 1000);
  const [active, setActive] = useState(false);

  useEffect(() => {
    let timer;
    let countdownInterval;

    const initIdleTimer = async () => {
      try {
        const res = await axios.get('http://localhost:3000/api/user-info', {
          withCredentials: true
        });

        if (!res.data || res.data.role !== 'admin') return;

        setActive(true);

        const startCountdown = () => {
          clearInterval(countdownInterval);
          setSecondsLeft(timeoutMs / 1000);

          countdownInterval = setInterval(() => {
            setSecondsLeft(prev => {
              if (prev <= 1) {
                clearInterval(countdownInterval);
                return 0;
              }
              return prev - 1;
            });
          }, 1000);
        };

        const resetTimer = () => {
          if (!active) return;
          clearTimeout(timer);
          clearInterval(countdownInterval);
          startCountdown();
          // makes sure admin logs out properly, by deleting cookies, go back to login
          timer = setTimeout(async () => {
            try {
              await axios.post('http://localhost:3000/api/logout', {}, { withCredentials: true });
            } catch (err) {
              console.warn('Logout failed:', err.message);
            }

            alert('Admin session expired due to inactivity.');
            localStorage.clear();
            navigate('/admin');
            window.location.reload();
          }, timeoutMs);
        };

        const events = ['mousemove', 'keydown', 'click', 'scroll'];
        events.forEach(event => window.addEventListener(event, resetTimer));

        resetTimer();

        return () => {
          clearTimeout(timer);
          clearInterval(countdownInterval);
          events.forEach(event => window.removeEventListener(event, resetTimer));
        };
      } catch (err) {
        console.warn('Idle logout setup failed:', err.message);
      }
    };

    initIdleTimer();
  }, [navigate, timeoutMs, active]);

  return secondsLeft;
};

export default useIdleLogout;
