import { useEffect, useState } from 'react'
import './css/App.css'
import Home from './pages/Home'
import Register from './pages/Register'
import Login from './pages/Login'
import Tasks from './pages/Tasks'
import NavBar from './components/NavBar'
import TaskFull from './pages/TaskFull'
import UpdateTask from './pages/UpdateTask'
import AllUsers from './pages/AllUsers'
import Logout from './pages/Logout'
import { Routes, Route } from 'react-router-dom'
import NewTask from './pages/NewTask'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div className="App">
      <NavBar />
      <main className="main-content">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/register" element={<Register />} />
          <Route path="/login" element={<Login />} />
          <Route path="/tasks" element={<Tasks />} />
          <Route path="/task" element={<NewTask />} />
          <Route path="/tasks/:id" element={<TaskFull />} />
          <Route path="/tasks/:id/edit" element={<UpdateTask />} />
          <Route path="/all_users" element={<AllUsers />} />
          <Route path="/logout" element={<Logout />} />
        </Routes>
      </main>
    </div>
  )
}

export default App

