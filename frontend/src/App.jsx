import { useEffect, useState } from "react";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [incidents, setIncidents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const [formData, setFormData] = useState({
    title: "",
    description: "",
    severity: "medium",
    service_name: "",
  });

  function loadIncidents() {
    setLoading(true);

    fetch(`${API_URL}/incidents`)
      .then((response) => {
        if (!response.ok) {
          throw new Error("Unable to load incidents");
        }

        return response.json();
      })
      .then((data) => {
        setIncidents(data);
        setLoading(false);
      })
      .catch((error) => {
        setError(error.message);
        setLoading(false);
      });
  }

  useEffect(() => {
    loadIncidents();
  }, []);

  function handleInputChange(event) {
    const { name, value } = event.target;

    setFormData({
      ...formData,
      [name]: value,
    });
  }

  async function createIncident(event) {
    event.preventDefault();

    setError("");
    setMessage("");

    try {
      const response = await fetch(`${API_URL}/incidents`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error("Unable to create incident");
      }

      setFormData({
        title: "",
        description: "",
        severity: "medium",
        service_name: "",
      });

      setMessage("Incident created successfully.");
      loadIncidents();
    } catch (error) {
      setError(error.message);
    }
  }

  async function updateStatus(incidentId, newStatus) {
    setError("");
    setMessage("");

    try {
      const response = await fetch(
        `${API_URL}/incidents/${incidentId}/status`,
        {
          method: "PATCH",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            status: newStatus,
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Unable to update incident status");
      }

      setMessage("Incident status updated successfully.");
      loadIncidents();
    } catch (error) {
      setError(error.message);
    }
  }

  return (
    <div
      style={{
        minHeight: "100vh",
        backgroundColor: "#f4f7fb",
        padding: "40px",
        fontFamily: "Arial, sans-serif",
      }}
    >
      <h1 style={{ color: "#172554" }}>
        OpsPilot Incident Dashboard
      </h1>

      <p style={{ color: "#64748b" }}>
        Monitor and manage enterprise incidents
      </p>

      <div
        style={{
          backgroundColor: "white",
          padding: "24px",
          borderRadius: "12px",
          marginBottom: "24px",
          boxShadow: "0 4px 12px rgba(0, 0, 0, 0.08)",
        }}
      >
        <h2>Create Incident</h2>

        <form onSubmit={createIncident}>
          <input
            name="title"
            placeholder="Incident title"
            value={formData.title}
            onChange={handleInputChange}
            required
            style={inputStyle}
          />

          <textarea
            name="description"
            placeholder="Incident description"
            value={formData.description}
            onChange={handleInputChange}
            required
            style={inputStyle}
          />

          <input
            name="service_name"
            placeholder="Service name"
            value={formData.service_name}
            onChange={handleInputChange}
            required
            style={inputStyle}
          />

          <select
            name="severity"
            value={formData.severity}
            onChange={handleInputChange}
            style={inputStyle}
          >
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="critical">Critical</option>
          </select>

          <button type="submit" style={buttonStyle}>
            Create Incident
          </button>
        </form>

        {message && (
          <p style={{ color: "green" }}>
            {message}
          </p>
        )}

        {error && (
          <p style={{ color: "red" }}>
            {error}
          </p>
        )}
      </div>

      <div
        style={{
          backgroundColor: "white",
          padding: "24px",
          borderRadius: "12px",
          boxShadow: "0 4px 12px rgba(0, 0, 0, 0.08)",
        }}
      >
        <h2>Incidents</h2>

        {loading && <p>Loading incidents...</p>}

        {!loading && incidents.length === 0 && (
          <p>No incidents found.</p>
        )}

        {!loading && incidents.length > 0 && (
          <table
            style={{
              width: "100%",
              borderCollapse: "collapse",
              marginTop: "20px",
            }}
          >
            <thead>
              <tr style={{ textAlign: "left" }}>
                <th style={cellStyle}>ID</th>
                <th style={cellStyle}>Title</th>
                <th style={cellStyle}>Service</th>
                <th style={cellStyle}>Severity</th>
                <th style={cellStyle}>Status</th>
		<th style={cellStyle}>Update Status</th>
              </tr>
            </thead>

            <tbody>
              {incidents.map((incident) => (
                <tr key={incident.id}>
                  <td style={cellStyle}>{incident.id}</td>
                  <td style={cellStyle}>{incident.title}</td>
                  <td style={cellStyle}>
                    {incident.service_name}
                  </td>
                  <td style={cellStyle}>{incident.severity}</td>
		<td style={cellStyle}>
  {incident.status}
</td>

<td style={cellStyle}>
  <select
    value={incident.status}
    onChange={(event) =>
      updateStatus(
        incident.id,
        event.target.value
      )
    }
    style={{
      padding: "8px",
      borderRadius: "6px",
      border: "1px solid #cbd5e1",
    }}
  >
    <option value="open">Open</option>
    <option value="investigating">
      Investigating
    </option>
    <option value="resolved">Resolved</option>
    <option value="closed">Closed</option>
  </select>
</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

const inputStyle = {
  display: "block",
  width: "100%",
  padding: "12px",
  marginBottom: "12px",
  border: "1px solid #cbd5e1",
  borderRadius: "8px",
  boxSizing: "border-box",
  fontSize: "15px",
};

const buttonStyle = {
  padding: "12px 20px",
  backgroundColor: "#2563eb",
  color: "white",
  border: "none",
  borderRadius: "8px",
  cursor: "pointer",
  fontSize: "15px",
};

const cellStyle = {
  padding: "12px",
  borderBottom: "1px solid #e2e8f0",
};

export default App;

