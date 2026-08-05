import { useEffect, useState, useRef } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import api from "../api/axios";

function GoogleCallback() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [error, setError] = useState("");
  const loginInitiated = useRef(false);

  useEffect(() => {
    if (loginInitiated.current) return;
    loginInitiated.current = true;

    const handleCallback = async () => {
      const code = searchParams.get("code");
      
      if (!code) {
        setError("Authorization code is missing from Google redirect.");
        return;
      }

      try {
        const response = await api.post("/auth/google", { code });
        // Save local JWT token
        localStorage.setItem("token", response.data.access_token);
        // Redirect to dashboard
        navigate("/dashboard", { replace: true });
      } catch (err) {
        setError(
          err.response?.data?.detail || 
          "Failed to verify Google login. Please try again."
        );
        console.error(err);
      }
    };

    handleCallback();
  }, [searchParams, navigate]);


  return (
    <div className="login-container">
      <div className="login-card text-center">
        <h1>RetailEye AI</h1>
        <p>Completing Google Authentication...</p>
        
        {error ? (
          <div className="error-section">
            <div className="error-alert">{error}</div>
            <button 
              className="btn btn-primary" 
              style={{ width: "100%", marginTop: "10px" }}
              onClick={() => navigate("/", { replace: true })}
            >
              Back to Login
            </button>
          </div>
        ) : (
          <div className="loading-spinner-container">
            <div className="loading-state">Securing connection & verifying credentials...</div>
          </div>
        )}
      </div>
    </div>
  );
}

export default GoogleCallback;
