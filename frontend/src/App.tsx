import { Navigate, Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import DashboardPage from "./pages/Dashboard";
import MapPage from "./pages/MapPage";
import CallsPage from "./pages/CallsPage";
import NewCallPage from "./pages/NewCallPage";
import AnalyzePage from "./pages/AnalyzePage";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/harita" element={<MapPage />} />
        <Route path="/cagrilar" element={<CallsPage />} />
        <Route path="/yeni" element={<NewCallPage />} />
        <Route path="/analiz" element={<AnalyzePage />} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Route>
    </Routes>
  );
}
