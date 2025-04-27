import '../css/TaskCard.css';

function TaskCard({ task, onClick }) {
  const truncateText = (text, maxLength) => {
    if (!text) return "No description";
    return text.length > maxLength ? text.slice(0, maxLength).trimEnd() + "..." : text;
  };

  const getPriorityLabel = (priority) => {
    switch (priority) {
      case 1:
        return { priorityLabel: "High", color: "#e74c3c" };     // red
      case 2:
        return { priorityLabel: "Medium", color: "#f39c12" };   // orange
      case 3:
        return { priorityLabel: "Low", color: "#27ae60" };      // green
      default:
        return { priorityLabel: "Unknown", color: "#7f8c8d" };  // grey
    }
  };

  const statusLabels = (status) => {
    status = parseInt(status);
    switch (status) {
      case 1:
        return { statusLabel: "Pending", color: "#f39c12" }; // orange
      case 2:
        return { statusLabel: "In Progress", color: "#3498db" }; // blue
      case 3:
        return { statusLabel: "Completed", color: "#27ae60" }; // green
      default:
        return { statusLabel: "Unknown", color: "#7f8c8d" }; // grey
    }
  };

  const { priorityLabel, color } = getPriorityLabel(task.priority);

  return (
    <div className="task-card" onClick={onClick}>
      <div className="task-header">
        <h2 className="task-title">{truncateText(task.title, 20)}</h2>
        <div className="task-meta">
          <span>Due: {task.due_date}</span>
          <span style={{ color: color }}> {priorityLabel}</span>
          <span>{statusLabels(task.status).statusLabel}</span>
        </div>
      </div>
      <div className="task-description">{truncateText(task.description, 60)}</div>
    </div>
  );
}

export default TaskCard