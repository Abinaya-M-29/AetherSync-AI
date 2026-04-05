import { Box } from '@mui/material';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import TopBar from './TopBar';

const drawerWidth = 240;

export default function Shell() {
  return (
    <Box sx={{ 
      display: 'flex', 
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #fdfcfb 0%, #e2d1c3 100%)', // Soft Peach/Grey Pastel
      // Alternative: 'linear-gradient(120deg, #e0c3fc 0%, #8ec5fc 100%)' // Soft Blue/Purple
      // Alternative: 'linear-gradient(to top, #cfd9df 0%, #e2ebf0 100%)' // Light Blue/Grey
      backgroundAttachment: 'fixed'
    }}>
      <TopBar drawerWidth={drawerWidth} />
      <Sidebar drawerWidth={drawerWidth} />
      
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          mt: 8,
          zIndex: 1
        }}
      >
        <Outlet />
      </Box>
    </Box>
  );
}
