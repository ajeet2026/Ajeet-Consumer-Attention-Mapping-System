import { Navigate, Outlet } from "react-router-dom";

export function parseJwt(token) {
  try {
    return JSON.parse(atob(token.split(".")[1]));
  } catch (e) {
    return null;
  }
}

function isTokenValid(token) {
  if (!token) return false;
  const payload = parseJwt(token);
  if (!payload) return false;
  // Check expiry — JWT "exp" is in seconds
  if (payload.exp && Date.now() >= payload.exp * 1000) {
    localStorage.removeItem("token");
    return false;
  }
  return true;
}

function ProtectedRoute({ allowedRoles }) {
  const token = localStorage.getItem("token");

  if (!isTokenValid(token)) {
    localStorage.removeItem("token");
    return <Navigate to="/" replace />;
  }

  if (allowedRoles) {
    const payload = parseJwt(token);
    if (!payload || !allowedRoles.includes(payload.role)) {
      return <Navigate to="/dashboard" replace />;
    }
  }

  return <Outlet />;
}

export default ProtectedRoute;
