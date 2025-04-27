import "../css/Login.css"
import { useState } from "react"
import { useNavigate } from "react-router-dom";
import api from '../api.js'

function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [errorVisible, setErrorVisible] = useState(false);
  const navigate = useNavigate();

  const handleLoginClick = async (e) => {
    e.preventDefault();
    try {
      const params = new URLSearchParams();
      params.append('username', username);
      params.append('password', password);
      const response = await api.post('/login', params);
      const token = response.data.access_token;

      sessionStorage.setItem('token', token);
      sessionStorage.setItem("id", response.data.id);
      setErrorVisible(false);
      navigate('/tasks');
    } catch (error) {
      console.error("login failed", error);
      setErrorVisible(true);
    }
  };

  return (
    <>
      <h1>Login</h1>
      <form onSubmit={handleLoginClick}>
        <div className="input-container">

          <input type="text" placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} />
          <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} />
        </div>
        <div className="button-container">

          <button type="submit" >Login</button>
          <button type="button" onClick={() => navigate('/')}>Back</button>
        </div>
      </form>
      {errorVisible && (
        <p style={{ color: 'red', marginBottom: '1em' }}>
          Invalid username or password.
        </p>
      )}
    </>
  );
}

export default Login

// ! done