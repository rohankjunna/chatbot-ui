import { useEffect, useState } from "react";

export default function AdminPanel() {
  const [leads, setLeads] = useState([]);
  const [search, setSearch] = useState("");

  // 🔥 Fetch leads (auto refresh)
  useEffect(() => {
    const fetchLeads = () => {
      fetch("http://localhost:8000/leads")
        .then(res => res.json())
        .then(data => {
          console.log("Leads:", data);
          setLeads(Array.isArray(data) ? data : []);
        })
        .catch(err => {
          console.error(err);
          setLeads([]);
        });
    };

    fetchLeads();
    const interval = setInterval(fetchLeads, 3000);

    return () => clearInterval(interval);
  }, []);

  // 🔥 Search filter
  const filteredLeads = leads.filter(l =>
    (l.subject || "").toLowerCase().includes(search.toLowerCase()) ||
    (l.city || "").toLowerCase().includes(search.toLowerCase()) ||
    (l.class || "").toLowerCase().includes(search.toLowerCase())
  );

  // 🔥 Stats
  const total = leads.length;
  const online = leads.filter(l => (l.mode || "").toLowerCase().includes("online")).length;
  const home   = total - online;

  return (
    <div style={{ padding: "20px", fontFamily: "Arial" }}>

      {/* 🔥 HEADER */}
      <h2>📊 Admin Dashboard</h2>

      {/* 🔥 STATS */}
      <div style={{ display: "flex", gap: "20px", marginBottom: "20px" }}>
        <div style={card}>Total Leads: {total}</div>
        <div style={card}>Online: {online}</div>
        <div style={card}>Home: {home}</div>
      </div>

      {/* 🔥 SEARCH */}
      <input
        style={input}
        placeholder="Search by subject, city, class..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
      />

      {/* 🔥 EXPORT BUTTON */}
      <button
        style={btn}
        onClick={() => window.open("http://localhost:8000/export")}
      >
        📥 Export Excel
      </button>

      {/* 🔥 TABLE */}
      <table style={table}>
        <thead>
          <tr>
            <th>ID</th>
            <th>Class</th>
            <th>Subject</th>
            <th>City</th>
            <th>Mode</th>
            <th>Contact</th>
            <th>Status</th>
          </tr>
        </thead>

        <tbody>
          {filteredLeads.length > 0 ? (
            filteredLeads.map((r, i) => (
              <tr key={i}>
                <td>{r.id}</td>
                <td>{r.class || "—"}</td>
                <td>{r.subject || "—"}</td>
                <td>{r.city || "—"}</td>
                <td>{r.mode || "—"}</td>
                <td>{r.contact || "—"}</td>
                <td>{r.status || "New"}</td>
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan="6">No leads found</td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}

// 🎨 Styles
const card = {
  padding: "15px",
  background: "#f2f2f2",
  borderRadius: "10px",
  fontWeight: "bold"
};

const input = {
  padding: "10px",
  width: "300px",
  marginBottom: "15px",
  borderRadius: "5px",
  border: "1px solid #ccc"
};

const btn = {
  marginLeft: "10px",
  padding: "10px 15px",
  background: "red",
  color: "white",
  border: "none",
  borderRadius: "5px",
  cursor: "pointer"
};

const table = {
  width: "100%",
  borderCollapse: "collapse"
};