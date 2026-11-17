import Chatbot from "./Chatbot";
import AdminPanel from "./AdminPanel";
import "./App.css";

function App() {
  return (
    <div style={{ background: "#cdd9fa", minHeight: "100vh" }}>
      
      {/* Admin Panel */}
      <AdminPanel />

      {/* Chatbot (floating) */}
      <Chatbot />

    </div>
  );
}

export default App;
