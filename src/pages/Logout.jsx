import { use, useEffect } from "react";
import { useNavigate } from "react-router-dom";

function Logout() {
    const navigate = useNavigate();

    useEffect(() => {
        const handleOnLogout = () => {
            sessionStorage.removeItem('token');
            sessionStorage.removeItem('id');
            navigate('/home');
        }

        handleOnLogout();
    }, [navigate]);

    return (
        <div>
            <h1>Logging Out</h1>
        </div>
    );
}

export default Logout