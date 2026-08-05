import { useNavigate, useLocation, Link } from "react-router-dom";
import { parseJwt } from "./ProtectedRoute";

function Layout({ children }) {
  const navigate = useNavigate();
  const location = useLocation();
  const token = localStorage.getItem("token");
  
  let userName = "User";
  let userRole = "Staff";
  
  if (token) {
    const payload = parseJwt(token);
    if (payload) {
      userName = payload.sub || "User";
      userRole = payload.role || "Staff";
    }
  }

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/", { replace: true });
  };

  const navItems = [
    { path: "/dashboard", label: "📊 Dashboard" },
    { path: "/stores", label: "🏪 Stores" },
    { path: "/shelves", label: "🗄️ Shelves" },
    { path: "/cameras", label: "🎥 Cameras" },
    { path: "/products", label: "📦 Products" },
  ];

  return (
    <div className="layout-container">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-brand">
          <h2>🛒 RetailEye AI</h2>
          <span className="brand-subtitle">Attention Mapping</span>
        </div>
        
        <nav className="sidebar-nav">
          <ul>
            {navItems.map((item) => {
              const isActive = location.pathname === item.path;
              return (
                <li key={item.path}>
                  <Link 
                    to={item.path} 
                    className={`nav-link ${isActive ? "active" : ""}`}
                  >
                    {item.label}
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>

        <div className="sidebar-footer">
          <button onClick={handleLogout} className="logout-btn">
            🚪 Logout
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="main-content">
        {/* Top Header */}
        <header className="top-header">
          <div className="header-title">
            <h1>{navItems.find(n => n.path === location.pathname)?.label.substring(3) || "Overview"}</h1>
          </div>
          <div className="user-profile">
            <span className={`role-badge role-${userRole.toLowerCase().replace(" ", "-")}`}>
              {userRole}
            </span>
            <span className="user-name">{userName}</span>
          </div>
        </header>

        {/* Content Body */}
        <main className="content-body">
          {children}
        </main>
      </div>
    </div>
  );
}

export default Layout;
