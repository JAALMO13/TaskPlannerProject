{/* 
    task planner header
    login btn
    register btn
*/}
import "../css/Home.css"
import { useNavigate } from "react-router-dom"

function Home() {
  const navigate = useNavigate();

  const handleLoginClick = () => {
    navigate('/login');
  }
  const handleRegisterClick = () => {
    navigate('/register');
  }
  return (
    <div className="home-container">
        <h1>Task Planner</h1>
        <div className="button-container">
          <button onClick={handleLoginClick}>Login</button>
          <button onClick={handleRegisterClick}>Register</button>
        </div>
    </div>
  )
}

export default Home