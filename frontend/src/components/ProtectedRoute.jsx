import { Navigate, Outlet } from "react-router-dom";

export function parseJwt(token) {
  try {
    return JSON.parse(atob(token.split(".")[1]));
  } catch (e) {
    return null;
  }
}

function ProtectedRoute({ allowedRoles }) {
  const token = localStorage.getItem("token");

  if (!token) {
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
