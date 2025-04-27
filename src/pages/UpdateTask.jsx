import "../css/UpdateTask.css"
import { useEffect, useState } from "react"
import api from "../api.js"
import { useNavigate, useParams } from "react-router-dom";

function UpdateTask() {
    const [task, setTask] = useState(null);
    const { id } = useParams();
    const [title, setTitle] = useState("");
    const [description, setDescription] = useState("");
    const [priority, setPriority] = useState("")
    const [dueDate, setDueDate] = useState("");
    const [status, setStatus] = useState("");
    const navigate = useNavigate();

    useEffect(() => {
        const getTask = async () => {
            try {
                const response = await api.get(`/tasks/${id}`);
                setTask(response.data);
            } catch (error) {
                console.error("Failed to fetch task:", error.response?.data || error.message);
            }
        };
        getTask();
    }, [id])




    useEffect(() => {
        if (task) {
            setTitle(task.title);
            setDescription(task.description);
            setPriority(task.priority);
            setDueDate(task.due_date);
            setStatus(task.status);
        }
    }, [task]);

    const handleUpdateTask = async (e) => {
        e.preventDefault();
        try {
            const task = {
                "user_id": sessionStorage.getItem("id"),
                "title": title,
                "description": description,
                "priority": priority,
                "due_date": dueDate,
                "status": status
            }
            await api.put(`/tasks/${id}`, task);
            navigate("/tasks");
        } catch (error) {
            console.error("Failed to update task:", error.response?.data || error.message);
        }
    }
    return (
        <div>
            <h1>Update Task</h1>
            <div className="input-container-update">
                <div>
                    <div className="container-update">Title</div> {" "}
                    <input type="text" value={title} onChange={(e) => setTitle(e.target.value)} />
                </div>
                <div>
                    <div className="container-update">Description</div> {" "}
                    <input type="text" value={description} onChange={(e) => setDescription(e.target.value)} />
                </div>
                <div>
                    <div className="container-update">Due Date</div>{" "}
                    <input
                        type="date"
                        value={dueDate}
                        onChange={(e) => setDueDate(e.target.value)}
                    />
                </div>
            </div>
            <div className="select-container-update">
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
            <div className="button-container-update">
                <form onSubmit={handleUpdateTask}><button type="submit">Update</button></form>
                <form onSubmit={() => navigate("/tasks")}><button type="submit">Back</button></form>
            </div>
        </div>
    );
}

export default UpdateTask
