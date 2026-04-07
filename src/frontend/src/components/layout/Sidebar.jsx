import { Drawer, List, ListItem, ListItemButton, ListItemIcon, ListItemText, Toolbar, Box, Typography } from '@mui/material';
import DashboardIcon from '@mui/icons-material/Dashboard';
import InventoryIcon from '@mui/icons-material/Inventory';
import ForestIcon from '@mui/icons-material/Forest';
import ListAltIcon from '@mui/icons-material/ListAlt';

import { useLocation, useNavigate } from 'react-router-dom';

export default function Sidebar({ drawerWidth }) {
  const location = useLocation();
  const navigate = useNavigate();

  const menuItems = [
    { text: 'Dashboard', icon: <DashboardIcon />, path: '/dashboard' },
    { text: 'Inventory', icon: <InventoryIcon />, path: '/inventory' },
    { text: 'Sustainability', icon: <ForestIcon />, path: '/sustainability' },
    { text: 'Activity Logs', icon: <ListAltIcon />, path: '/activity' },

  ];

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        [`& .MuiDrawer-paper`]: {
          width: drawerWidth,
          boxSizing: 'border-box',
          backgroundColor: 'rgba(255, 255, 255, 0.4)',
          backdropFilter: 'blur(20px)',
          borderRight: '1px solid rgba(255, 255, 255, 0.3)',
        },
      }}
    >
      <Toolbar sx={{ px: 3, pt: 2, pb: 1 }}>
        <Typography variant="h5" color="primary" sx={{
          fontWeight: 900,
          letterSpacing: '-0.05em',
          background: 'linear-gradient(45deg, #2E7D32 30%, #1976D2 90%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
        }}>
          AetherSync
        </Typography>
      </Toolbar>
      <Box sx={{ overflow: 'auto', mt: 2 }}>
        <List>
          {menuItems.map((item) => {
            const isSelected = location.pathname.startsWith(item.path);
            return (
              <ListItem key={item.text} disablePadding sx={{ mb: 1, px: 2 }}>
                <ListItemButton
                  selected={isSelected}
                  onClick={() => navigate(item.path)}
                  sx={{
                    borderRadius: 3,
                    py: 1.5,
                    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                    '&:hover': {
                      backgroundColor: 'rgba(25, 118, 210, 0.08)',
                      transform: 'translateX(4px)',
                    },
                    ...(isSelected && {
                      backgroundColor: 'rgba(25, 118, 210, 0.12) !important',
                      color: 'secondary.main',
                      boxShadow: '0 4px 12px rgba(25, 118, 210, 0.1)',
                    })
                  }}
                >
                  <ListItemIcon sx={{
                    color: isSelected ? 'secondary.main' : 'inherit',
                    minWidth: 42,
                    transition: 'all 0.3s'
                  }}>
                    {item.icon}
                  </ListItemIcon>
                  <ListItemText
                    primary={item.text}
                    primaryTypographyProps={{
                      fontWeight: isSelected ? 800 : 500,
                      fontSize: '0.92rem',
                      letterSpacing: '0.01em'
                    }}
                  />
                </ListItemButton>
              </ListItem>
            );
          })}
        </List>
      </Box>
    </Drawer>
  );
}
