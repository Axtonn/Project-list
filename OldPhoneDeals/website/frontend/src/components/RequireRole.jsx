import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

// checks if people entering admin is an admin, sends them back to home if not admin
const RequireRole = ({ role = null, children }) => {
  const navigate = useNavigate();
  const [checked, setChecked] = useState(false);

  useEffect(() => {
    const verify = async () => {
      try {
        const res = await axios.get('http://localhost:3000/api/user/user-info', {
          withCredentials: true,
        });

        if (role && res.data.role !== role) {
          console.log('This page is for admins to view only')
          return navigate('/', { replace: true });
        }

        setChecked(true);
      } catch {
        console.log('This page is for admins to view only')
        navigate('/', { replace: true });
      }
    };

    verify();
  }, [navigate, role]);

  if (!checked) return null;
  return <>{children}</>;
};

export default RequireRole;
