import { Routes, Route } from "react-router-dom";

import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Stores from "./pages/Stores";
import Products from "./pages/Products";
import Shelves from "./pages/Shelves";
import Cameras from "./pages/Cameras";
import NotFound from "./pages/NotFound";
import ProtectedRoute from "./components/ProtectedRoute";
import Layout from "./components/Layout";
import GoogleCallback from "./pages/GoogleCallback";
import BehaviorAnalytics from "./components/BehaviorAnalytics";
import ProductAnalytics from "./components/ProductAnalytics";

function App() {
  return (
    <Routes>
      {/* Public Login Route */}
      <Route path="/" element={<Login />} />
      <Route path="/auth/callback" element={<GoogleCallback />} />

      {/* Protected Views */}
      <Route element={<ProtectedRoute />}>
        <Route 
          path="/dashboard" 
          element={
            <Layout>
              <Dashboard />
            </Layout>
          } 
        />
        <Route 
          path="/stores" 
          element={
            <Layout>
              <Stores />
            </Layout>
          } 
        />
        <Route 
          path="/products" 
          element={
            <Layout>
              <Products />
            </Layout>
          } 
        />
        <Route 
          path="/shelves" 
          element={
            <Layout>
              <Shelves />
            </Layout>
          } 
        />
        <Route 
          path="/cameras" 
          element={
            <Layout>
              <Cameras />
            </Layout>
          } 
        />
        <Route 
          path="/behavior" 
          element={
            <Layout>
              <BehaviorAnalytics />
            </Layout>
          } 
        />
        <Route 
          path="/analytics/products" 
          element={
            <Layout>
              <ProductAnalytics />
            </Layout>
          } 
        />
      </Route>

      {/* 404 Not Found */}
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}

export default App;