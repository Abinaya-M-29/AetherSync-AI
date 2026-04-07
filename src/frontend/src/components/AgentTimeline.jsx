import { useState } from 'react';
import { Timeline, TimelineItem, TimelineSeparator, TimelineConnector, TimelineContent, TimelineDot } from '@mui/lab';
import { Typography, Box, Chip, Dialog, DialogTitle, DialogContent, DialogActions, Button, Divider, Paper } from '@mui/material';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import HourglassEmptyIcon from '@mui/icons-material/HourglassEmpty';

// Map API status → MUI chip color
function statusColor(status) {
  if (status === 'completed') return 'success';
  if (status === 'failed') return 'error';
  if (status === 'running') return 'warning';
  return 'primary';
}

// Map API status → chip variant
function statusVariant(status) {
  return status === 'running' ? 'outlined' : 'filled';
}

// Map status → icon
function StatusIcon({ status }) {
  if (status === 'completed') return <CheckCircleIcon fontSize="small" />;
  if (status === 'failed') return <ErrorIcon fontSize="small" />;
  if (status === 'running') return <HourglassEmptyIcon fontSize="small" />;
  return <SmartToyIcon fontSize="small" />;
}

// Format ISO timestamp to readable time string
function formatTime(isoStr) {
  if (!isoStr) return '';
  try {
    const safeStr = isoStr.replace(' ', 'T') + (isoStr.endsWith('Z') ? '' : 'Z');
    return new Date(safeStr).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  } catch {
    return isoStr;
  }
}

function formatDateTime(isoStr) {
  if (!isoStr) return '—';
  try {
    const safeStr = isoStr.replace(' ', 'T') + (isoStr.endsWith('Z') ? '' : 'Z');
    return new Date(safeStr).toLocaleString([], {
      month: 'short', day: 'numeric',
      hour: '2-digit', minute: '2-digit', second: '2-digit'
    });
  } catch {
    return isoStr;
  }
}

export default function AgentTimeline({ tasks = [], onAction }) {
  const [selectedTask, setSelectedTask] = useState(null);

  if (!tasks || tasks.length === 0) {
    return (
      <Box sx={{ py: 4, textAlign: 'center' }}>
        <Typography variant="body2" color="text.secondary">
          No agent activity yet. Trigger an agent to see logs here.
        </Typography>
      </Box>
    );
  }

  return (
    <>
      <Timeline sx={{ p: 0, m: 0 }}>
        {tasks.map((task, index) => {
          const isLast = index === tasks.length - 1;
          const color = statusColor(task.status);
          const variant = statusVariant(task.status);

          return (
            <TimelineItem
              key={task.run_id || index}
              sx={{
                minHeight: 60,
                '&::before': { display: 'none' },
                cursor: 'pointer',
                borderRadius: 1,
                '&:hover': { bgcolor: 'action.hover' },
                transition: 'background 0.15s',
              }}
              onClick={() => setSelectedTask(task)}
            >
              <TimelineSeparator>
                <TimelineDot color={color} variant={variant}>
                  <StatusIcon status={task.status} />
                </TimelineDot>
                {!isLast && <TimelineConnector />}
              </TimelineSeparator>
              <TimelineContent sx={{ py: '12px', px: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <Box>
                    <Typography variant="body2" fontWeight="bold" component="span">
                      {task.agent_name || 'Agent'}:
                    </Typography>
                    <Typography variant="body2" color="text.secondary" component="span" sx={{ ml: 1 }}>
                      {task.domain || 'unknown'}
                    </Typography>
                  </Box>
                  <Typography variant="caption" color="text.secondary">
                    {formatTime(task.started_at)}
                  </Typography>
                </Box>

                <Box sx={{ mt: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Chip
                    label={task.status}
                    size="small"
                    color={color}
                    variant={variant}
                    sx={{ height: 20, fontSize: '0.7rem' }}
                  />
                  {task.response && (
                    <Typography variant="caption" color="text.secondary" noWrap sx={{ maxWidth: 180 }}>
                      {task.response.substring(0, 60)}…
                    </Typography>
                  )}
                </Box>
              </TimelineContent>
            </TimelineItem>
          );
        })}
      </Timeline>

      {/* Run Detail Dialog */}
      <Dialog
        open={!!selectedTask}
        onClose={() => setSelectedTask(null)}
        maxWidth="sm"
        fullWidth
        PaperProps={{ sx: { borderRadius: 3, bgcolor: '#ffffff' } }}
      >
        {selectedTask && (
          <>
            <DialogTitle sx={{ pb: 1 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <StatusIcon status={selectedTask.status} />
                <Typography variant="h6" fontWeight="bold">
                  {selectedTask.agent_name || 'Agent'}: {selectedTask.domain}
                </Typography>
                <Chip
                  label={selectedTask.status}
                  size="small"
                  color={statusColor(selectedTask.status)}
                  sx={{ ml: 'auto' }}
                />
              </Box>
              <Typography variant="caption" color="text.secondary">
                {formatDateTime(selectedTask.started_at)} → {formatDateTime(selectedTask.finished_at)}
              </Typography>
            </DialogTitle>

            <DialogContent dividers>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                {/* Input */}
                <Box>
                  <Typography variant="overline" color="primary" display="block" gutterBottom>
                    Trigger Input
                  </Typography>
                  <Paper variant="outlined" sx={{ p: 1.5, bgcolor: '#f5f5f5' }}>
                    <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                      {selectedTask.input || '—'}
                    </Typography>
                  </Paper>
                </Box>

                <Divider />

                {/* Response */}
                <Box>
                  <Typography
                    variant="overline"
                    color={selectedTask.status === 'failed' ? 'error' : 'success.main'}
                    display="block"
                    gutterBottom
                  >
                    Agent Response
                  </Typography>
                  {selectedTask.error && (
                    <Paper variant="outlined" sx={{ p: 1.5, bgcolor: '#f5f5f5' }}>
                      <Typography variant="body2" color="error">
                        <strong>Error:</strong> {selectedTask.error}
                      </Typography>
                    </Paper>
                  )}
                  <Paper variant="outlined" sx={{ p: 1.5, bgcolor: '#f5f5f5' }}>
                    <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap', lineHeight: 1.8 }}>
                      {selectedTask.response || 'No response recorded for this run.'}
                    </Typography>
                  </Paper>
                </Box>
              </Box>
            </DialogContent>

            <DialogActions>
              <Button onClick={() => setSelectedTask(null)} variant="contained" size="small">
                Close
              </Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </>
  );
}
