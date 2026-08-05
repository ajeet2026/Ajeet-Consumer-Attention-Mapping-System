import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/axios";

function Login() {
    const navigate = useNavigate();

    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const handleLogin = async (e) => {
        e.preventDefault();

        setLoading(true);
        setError("");

        try {
            const response = await api.post(
                "/auth/login",
                new URLSearchParams({
                    username: email,
                    password: password,
                }),
                {
                    headers: {
                        "Content-Type": "application/x-www-form-urlencoded",
                    },
                }
            );

            // Save JWT Token
            localStorage.setItem(
                "token",
                response.data.access_token
            );

            // Redirect to Dashboard
            navigate("/dashboard");

        } catch (err) {
            setError(
                err.response?.data?.detail ||
                "Invalid Email or Password"
            );
        } finally {
            setLoading(false);
        }
    };

    const handleGoogleLogin = () => {
        const clientId = "239269367990-g1tksjreouhujr0ur907tqu402to8l8i.apps.googleusercontent.com";
        const redirectUri = "http://localhost:5173/auth/callback";
        const googleAuthUrl = `https://accounts.google.com/o/oauth2/v2/auth?` +
            `client_id=${clientId}&` +
            `redirect_uri=${encodeURIComponent(redirectUri)}&` +
            `response_type=code&` +
            `scope=${encodeURIComponent("openid email profile")}&` +
            `prompt=select_account`;
        window.location.href = googleAuthUrl;
    };


    return (
        <div className="login-container">

            <form
                className="login-card"
                onSubmit={handleLogin}
            >

                <h1>Consumer Attention Mapping System</h1>

                <p>AI Powered Retail Analytics Dashboard</p>

                <label>Email Address</label>

                <input
                    type="email"
                    placeholder="Enter your email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                />

                <label>Password</label>

                <input
                    type="password"
                    placeholder="Enter your password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                />

                <div className="remember">
                    <input type="checkbox" />
                    <span>Remember Me</span>
                </div>

                {error && (
                    <p className="error">
                        {error}
                    </p>
                )}

                <button
                    type="submit"
                    disabled={loading}
                >
                    {loading ? "Logging In..." : "Login"}
                </button>

                <div className="divider">
                    <span>or</span>
                </div>

                <button
                    type="button"
                    className="google-login-btn"
                    onClick={handleGoogleLogin}
                    disabled={loading}
                >
                    <svg className="google-icon" viewBox="0 0 24 24" width="20" height="20">
                        <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                        <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                        <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"/>
                        <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/>
                    </svg>
                    Continue with Google
                </button>

                <small>
                    Secure Authentication using JWT
                </small>

            </form>

        </div>
    );
}

export default Login;