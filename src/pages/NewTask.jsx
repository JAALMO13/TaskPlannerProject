{/*
    title input field
    description input field
    due date calendar field
    priotity drop down
    status default pending    
*/}

import "../css/NewTask.css"
import { useState } from "react";
import api from "../api.js";
import { useNavigate } from "react-router-dom";

function NewTask() {
    const [title, setTitle] = useState("");
    const [description, setDescription] = useState("");
    const [priority, setPriority] = useState("1");
    const [dueDate, setDueDate] = useState("");
    const [status, setStatus] = useState("1");
    const navigate = useNavigate();



    const handleCreateNewTask = async (e) => {
        e.preventDefault();
        try {
            const task = {
                "user_id": 0,
                "title": title,
                "description": description,
                "priority": priority,
                "due_date": dueDate,
                "status": status
            }

            await api.post("/tasks", task);
            navigate("/tasks");
        } catch (error) {
            console.error("Failed to create task:", error.response?.data || error.message);
        }
    }

    return (
        <>
            <h1>New Task</h1>
            <div className="input-container-new-task">
                <div className="container-new-task">
                    <div>Title</div> {" "}
                    <input type="text" value={title} onChange={(e) => setTitle(e.target.value)} />
                </div>
                <div className="container-new-task">
                    <div>Description</div> {" "}
                    <input type="text" value={description} onChange={(e) => setDescription(e.target.value)} />
                </div>
                <div className="container-new-task">
                    <div>Due Date</div>{" "}
                    <input
                        type="date"
                        value={dueDate}
                        onChange={(e) => setDueDate(e.target.value)}
                    />
                </div>
            </div>
            <div className="select-container-new-task">
                <div>Priority</div>

                <select value={priority} onChange={(e) => setPriority(e.target.value)}>
                    <option value="1">High</option>
                    <option value="2">Medium</option>
                    <option value="3">Low</option>
                </select>
                <div>Status</div>
                <select value={status} onChange={(e) => setStatus(e.target.value)}>
                    <option value="1">Pending</option>
                    <option value="2">Comleted</option>
                </select>
            </div>
            <div className="button-container-new-task">
                <form onSubmit={handleCreateNewTask}><button type="submit">Create</button></form>
                <form onSubmit={() => navigate("/tasks")}><button type="submit">Back</button></form>
            </div>
        </>
    );

}

export default NewTask

// ! fix api