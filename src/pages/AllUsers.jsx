import api from "../api.js";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom"; 

function AllUsers() {
    const [users, setUsers] = useState([]);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchUsers = async () => {
            try {
                const response = await api.get('/users');
                setUsers(response.data);
            } catch (error) {
                console.error("Failed to fetch users:", error.response?.data || error.message);
                navigate('/');
            }
        };

        fetchUsers();
    }, []);

    return (
        <>
            <h1>All Users</h1>            
            {users.length === 0 ? <h2>No users found</h2> : users.map((user) => <h2 key={user.id}>{user.id} - {user.username}</h2>)}
        </>
    );
}

export default AllUsers