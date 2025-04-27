{/*
    view full description
        
*/}

import "../css/TaskFull.css"
import { useParams, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import api from "../api.js";

function TaskFull() {
    const { id } = useParams();
    const [task, setTask] = useState(null);
    const navigate = useNavigate();

    useEffect(() => {
        const getTask = async () => {
            try {
                const response = await api.get(`/tasks/${id}`);
                setTask(response.data);
            } catch (error) {
                console.error("Failed to fetch task:", error.response?.data || error.message);
                navigate('/tasks');
            }
        };

        getTask();
    }, [id, navigate]);

    const handleDeleteTask = async () => {
        try {
            await api.delete(`/tasks/${id}`);
            navigate('/tasks');
        } catch (error) {
            console.error("Failed to delete task:", error.response?.data || error.message);
        }
    };

    const handleUpdateTask = () => {
        navigate(`/tasks/${id}/edit`);
    };


    if (!task) return <p>Loading task...</p>;

    return (
        <div className="task-page">
            <div className="task-full">
                <h1 className="title">{task.title}</h1>
                <div className="top-row">

                    <p className="due-date">Due: {task.due_date}</p>
                    <p className="priority">Priority: {task.priority}</p>
                </div>
                <div className="description">{task.description}</div>
                <div className="bottom-row">
                    <p className="status">Status: {task.status}</p>
                </div>
            </div>
            <div className="button-container">
                <button onClick={handleUpdateTask}>Update</button>
                <button onClick={handleDeleteTask}>Delete</button>
                <button onClick={() => navigate('/tasks')}>Back</button>
            </div>
        </div>
    );
}


export default TaskFull