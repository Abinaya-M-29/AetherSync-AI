import { Dialog, DialogTitle, DialogContent, DialogActions, Button, Typography, Box, Chip } from '@mui/material';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';

export default function PermissionDialog({ open, onClose, task, gridStatus }) {
  if (!task) return null;

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth PaperProps={{ sx: { borderRadius: 2 } }}>
      <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1, color: 'warning.main', fontWeight: 'bold' }}>
        <WarningAmberIcon />
        Agent Permission Required
      </DialogTitle>
      <DialogContent dividers>
        <Typography variant="body1" sx={{ mb: 2 }}>
          <strong>Agent {task.agent}</strong> seeks permission to <strong>{task.task.toLowerCase()}</strong>.
        </Typography>
        
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2, p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
          <Typography variant="body2" color="text.secondary">Current Grid Status:</Typography>
          <Chip 
            label={gridStatus} 
            color={gridStatus === 'GREEN' ? 'success' : 'error'} 
            size="small" 
            sx={{ fontWeight: 'bold' }} 
          />
        </Box>

        <Typography variant="body2" color="text.secondary">
          Request Type: <Chip label={task.intention || "High-Energy"} size="small" variant="outlined" />
        </Typography>
      </DialogContent>
      <DialogActions sx={{ p: 2 }}>
        <Button onClick={onClose} color="inherit" variant="outlined">
          Reschedule
        </Button>
        <Button onClick={onClose} color="error" variant="contained" sx={{ boxShadow: 'none' }}>
          Deny
        </Button>
        <Button onClick={onClose} color="primary" variant="contained" autoFocus sx={{ boxShadow: 'none' }}>
          Approve
        </Button>
      </DialogActions>
    </Dialog>
  );
}
