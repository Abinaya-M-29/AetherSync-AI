import { useState, useEffect } from 'react';
import { 
  Box, Typography, Chip, Drawer, IconButton, Divider, 
  CircularProgress, Paper 
} from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import CloseIcon from '@mui/icons-material/Close';
import axios from 'axios';
import { useMetrics } from '../../hooks/useMetrics';

// Format ISO string to readable string
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

function calculateDuration(start, end) {
  if (!start || !end) return '—';
  const s1 = start.replace(' ', 'T') + (start.endsWith('Z') ? '' : 'Z');
  const s2 = end.replace(' ', 'T') + (end.endsWith('Z') ? '' : 'Z');
  const startTime = new Date(s1).getTime();
  const endTime = new Date(s2).getTime();
  const diffInSeconds = Math.max(0, Math.floor((endTime - startTime) / 1000));
  return `${diffInSeconds}s`;
}

export default function ActivityLogs() {
  const { activityLogs } = useMetrics();
  
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [selectedRunId, setSelectedRunId] = useState(null);
  const [runDetails, setRunDetails] = useState(null);
  const [detailsLoading, setDetailsLoading] = useState(false);

  const fetchRunDetails = async (runId) => {
    setDetailsLoading(true);
    setRunDetails(null);
    try {
      const res = await axios.get(`/api/activity/logs/${runId}`);
      setRunDetails(res.data);
    } catch (err) {
      console.error("Failed to fetch run details:", err);
    } finally {
      setDetailsLoading(false);
    }
  };

  const handleRowClick = (params) => {
    const runId = params.row.run_id;
    setSelectedRunId(runId);
    setDrawerOpen(true);
    fetchRunDetails(runId);
  };

  const columns = [
    { 
      field: 'agent_name', 
      headerName: 'Agent Model', 
      flex: 1, 
      minWidth: 150 
    },
    { 
      field: 'domain', 
      headerName: 'Domain', 
      flex: 1, 
      minWidth: 120 
    },
    {
      field: 'status',
      headerName: 'Status',
      width: 130,
      renderCell: (params) => {
        let color = 'primary';
        if (params.value === 'completed') color = 'success';
        if (params.value === 'failed') color = 'error';
        if (params.value === 'running') color = 'warning';
        return (
          <Chip 
            label={params.value || 'unknown'} 
            color={color} 
            size="small" 
            variant={params.value === 'running' ? 'outlined' : 'filled'}
            sx={{ fontWeight: 'bold' }}
          />
        );
      }
    },
    {
      field: 'started_at',
      headerName: 'Started At',
      flex: 1,
      minWidth: 180,
      valueFormatter: (value) => formatDateTime(value)
    },
    {
      field: 'finished_at',
      headerName: 'Finished At',
      flex: 1,
      minWidth: 180,
      valueFormatter: (value) => formatDateTime(value)
    },
    {
      field: 'duration',
      headerName: 'Duration',
      width: 100,
      valueGetter: (value, row) => calculateDuration(row.started_at, row.finished_at)
    }
  ];

  return (
    <Box sx={{ p: 2, height: 'calc(100vh - 88px)', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ mb: 2 }}>
        <Typography variant="h4" sx={{ fontWeight: 800 }}>
          Agent Activity Logs
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Detailed telemetry for all LangGraph orchestrations and subagent executions.
        </Typography>
      </Box>

      <Paper sx={{ flex: 1, overflow: 'hidden' }}>
        <DataGrid
          rows={activityLogs}
          columns={columns}
          getRowId={(row) => row.run_id || row.id}
          onRowClick={handleRowClick}
          sx={{
            border: 'none',
            '& .MuiDataGrid-cell:focus': { outline: 'none' },
            '& .MuiDataGrid-row:hover': { cursor: 'pointer' },
          }}
          disableRowSelectionOnClick
        />
      </Paper>

      {/* Detail Drawer */}
      <Drawer
        anchor="right"
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        PaperProps={{
          sx: { width: { xs: '100%', sm: 600 }, p: 3, backgroundColor: 'background.default' }
        }}
      >
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6" fontWeight="bold">Run Details</Typography>
          <IconButton onClick={() => setDrawerOpen(false)}>
            <CloseIcon />
          </IconButton>
        </Box>

        {detailsLoading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
            <CircularProgress />
          </Box>
        )}

        {!detailsLoading && runDetails && (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
            
            {/* Context Box */}
            <Paper variant="outlined" sx={{ p: 2, bgcolor: 'background.paper' }}>
              <Typography variant="overline" color="primary">User Input</Typography>
              <Typography variant="body1" sx={{ mt: 1, whiteSpace: 'pre-wrap' }}>
                {runDetails.input}
              </Typography>
            </Paper>

            <Paper variant="outlined" sx={{ p: 2, bgcolor: 'background.paper' }}>
              <Typography variant="overline" color={runDetails.status === 'failed' ? 'error' : 'success'}>
                Final Response
              </Typography>
              {runDetails.error && (
                <Typography variant="body2" color="error" sx={{ mt: 1, mb: 1 }}>
                  <strong>Error:</strong> {runDetails.error}
                </Typography>
              )}
              <Typography variant="body1" sx={{ mt: 1, whiteSpace: 'pre-wrap' }}>
                {runDetails.response || 'No response recorded.'}
              </Typography>
            </Paper>

            <Divider />
            <Typography variant="h6" fontWeight="bold">Execution Steps</Typography>

            {(!runDetails.steps || runDetails.steps.length === 0) ? (
              <Typography variant="body2" color="text.secondary">No steps recorded.</Typography>
            ) : (
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                {runDetails.steps.map((step, idx) => (
                  <Paper key={idx} variant="outlined" sx={{ p: 2, borderLeft: 4, borderColor: 'primary.main' }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="subtitle2" fontWeight="bold">
                        {step.step_type.toUpperCase()}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {formatDateTime(step.created_at)}
                      </Typography>
                    </Box>
                    <Typography variant="body2">
                      {step.description}
                    </Typography>
                    
                    {step.payload && (
                      <Box sx={{ mt: 1, p: 1, bgcolor: 'action.hover', borderRadius: 1, overflowX: 'auto' }}>
                        <Typography variant="caption" component="pre" sx={{ m: 0 }}>
                          {JSON.stringify(JSON.parse(step.payload), null, 2)}
                        </Typography>
                      </Box>
                    )}
                  </Paper>
                ))}
              </Box>
            )}

          </Box>
        )}
      </Drawer>
    </Box>
  );
}
