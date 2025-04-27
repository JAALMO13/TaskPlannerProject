import "../css/Tasks.css"
import { useEffect, useState } from 'react';
import TaskCard from '../components/TaskCard'
import api from '../api.js'
import { useNavigate } from 'react-router-dom';
function Tasks() {
    const [tasks, setTasks] = useState([]);
    const navigate = useNavigate();
    useEffect(() => {
        const getTasks = async () => {
            try {
                const response = await api.get('/tasks');
                sessionStorage.setItem("id", response.data.id); // user_id
                setTasks(response.data);
            } catch (error) {
                console.error("Failed to fetch tasks:", error.response?.data || error.message);
            }
        };

        getTasks();
    }, []);

    const handleCreateTask = () => {
        navigate('/task');
    }

    const handleTaskClick = (taskID) => {
        navigate(`/tasks/${taskID}`);
    }
    return (
        <>
            <h1>Tasks</h1>
            <div className="task-container">
               {tasks.length === 0 ? <p>No tasks found</p> : tasks.map((task) => <TaskCard key={task.id} task={task} onClick={() => handleTaskClick(task.id)}/>)}
            </div>
            <form onSubmit={handleCreateTask}>
                <button type='submit'>Create New Task</button>
            </form>
        </>
    );
}
export default Tasks
