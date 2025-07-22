import React, { useState } from 'react';
import SignIn from '../components/Signin';
import SignUp from '../components/Signup';

const Auth = () => {
  const [isSignin, setIsSignin] = useState(true);
  return (
    <>
      {isSignin ? <SignIn onToggle={() => setIsSignin(false)} isAdmin={false}/> : <SignUp onToggle={() => setIsSignin(true)}/>}
    </>
  );
};


export default Auth