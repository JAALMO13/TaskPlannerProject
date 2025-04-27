import "../css/Register.css"
import { useState } from "react"
import { useNavigate } from "react-router-dom";
import api from '../api.js'


function Register() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [passwordConfirm, setPasswordConfirm] = useState('');
  const [errorVisibleUser, setErrorVisibleUser] = useState(false);
  const [errorVisiblePass, setErrorVisiblePass] = useState(false);
  const navigate = useNavigate();

  const handleRegisterClick = async (e) => {
    e.preventDefault()
    try {

      if (password === passwordConfirm) {
        const params = new URLSearchParams();
        params.append('username', username);
        params.append('password', password);

        await api.post('/register', params);
        setErrorVisibleUser(false);
        setErrorVisiblePass(false);
        navigate('/login');
      }
      else {
        console.log("passwords do not match");
        setErrorVisibleUser(false);
        setErrorVisiblePass(true);
      }
    } catch (error) {
      console.error("register failed", error);
      setErrorVisiblePass(false);
      setErrorVisibleUser(true);
    }
  };

  return (
    <>
      <h1>Register</h1>
      <form onSubmit={handleRegisterClick}>
        <div className="input-container">
          <input type="text" placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} />
          <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} />
          <input type="password" placeholder="Confirm Password" value={passwordConfirm} onChange={(e) => setPasswordConfirm(e.target.value)} />
        </div>
        <div className="button-container">
          <button type="submit">Register</button>
          <button type="button" onClick={() => navigate('/')}>Back</button>
        </div>
      </form>
      {errorVisibleUser && (
        <p style={{ color: 'red', marginBottom: '1em' }}>
          Username already exists.
        </p>
      )}
      {errorVisiblePass && (
        <p style={{ color: 'red', marginBottom: '1em' }}>
          Passwords do not match
        </p>
      )}
    </>

  )
}

export default Register

// ! done
