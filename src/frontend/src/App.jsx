import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Shell from './components/layout/Shell';
import Dashboard from './components/views/Dashboard';
import Inventory from './components/views/Inventory';
import Sustainability from './components/views/Sustainability';
import ActivityLogs from './components/views/ActivityLogs';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Shell />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="inventory" element={<Inventory />} />
          <Route path="sustainability" element={<Sustainability />} />
          <Route path="activity" element={<ActivityLogs />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
