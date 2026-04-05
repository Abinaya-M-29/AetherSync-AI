import { AppBar, Toolbar, Typography, Box, Chip, Avatar, Skeleton } from '@mui/material';
import { useMetrics } from '../../hooks/useMetrics';

export default function TopBar({ drawerWidth }) {
  const { gridHealth, loading } = useMetrics();
  
  const isHealthy = gridHealth.status === 'GREEN';

  return (
    <AppBar
      position="fixed"
      sx={{
        width: { sm: `calc(100% - ${drawerWidth}px)` },
        ml: { sm: `${drawerWidth}px` },
        background: 'rgba(255, 255, 255, 0.4)',
        backdropFilter: 'blur(15px)',
        borderBottom: '1px solid rgba(255, 255, 255, 0.3)',
      }}
    >
      <Toolbar sx={{ px: 4 }}>
        <Box sx={{ flexGrow: 1, display: 'flex', alignItems: 'center', gap: 3 }}>
          <Typography variant="h6" noWrap component="div" sx={{ 
            color: 'text.primary', 
            fontWeight: 800,
            letterSpacing: '-0.02em'
          }}>
            Command Center
          </Typography>
          
          {loading ? (
            <Skeleton variant="rounded" width={100} height={32} sx={{ borderRadius: 2 }} />
          ) : (
            <Chip 
              label={`Grid: ${gridHealth.status}`} 
              color={isHealthy ? 'success' : 'error'}
              variant="filled"
              size="small"
              sx={{ 
                fontWeight: 800, 
                px: 1,
                borderRadius: '8px',
                background: isHealthy ? 'linear-gradient(135deg, #2E7D32 0%, #1B5E20 100%)' : undefined,
                boxShadow: isHealthy ? '0 4px 12px rgba(46, 125, 50, 0.2)' : '0 4px 12px rgba(211, 47, 47, 0.2)',
              }}
            />
          )}
        </Box>
        
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Typography variant="body2" color="text.secondary">
            Admin User
          </Typography>
          <Avatar sx={{ bgcolor: 'secondary.main', width: 36, height: 36 }}>A</Avatar>
        </Box>
      </Toolbar>
    </AppBar>
  );
}
