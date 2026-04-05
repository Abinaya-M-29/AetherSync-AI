import { Box, Card, CardContent, Typography, Button, Grid, Tooltip, Chip } from '@mui/material';
import { useMetrics } from '../../hooks/useMetrics';
import AgentTimeline from '../AgentTimeline';
import PermissionDialog from '../PermissionDialog';
import { useState } from 'react';
import { Gauge, gaugeClasses } from '@mui/x-charts/Gauge';
import Co2Icon from '@mui/icons-material/Co2';
import BoltIcon from '@mui/icons-material/Bolt';

export default function Dashboard() {
  const { gridHealth } = useMetrics();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [selectedTask, setSelectedTask] = useState(null);

  const handleActionRequired = (task) => {
    setSelectedTask(task);
    setDialogOpen(true);
  };

  const isHealthy = gridHealth.status === 'GREEN';

  return (
    <Box sx={{ p: 1, display: 'flex', flexDirection: 'column', height: 'calc(100vh - 88px)', gap: 2.5 }}>

      {/* Page Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexShrink: 0 }}>
        <Box>
          <Typography variant="h4" sx={{
            fontWeight: 900,
            letterSpacing: '-0.04em',
            mb: 0.5,
            background: 'linear-gradient(45deg, #1A2027 30%, #454C5E 90%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
          }}>
            The Pulse Overview
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Ecological orchestration and AI agent command center
          </Typography>
        </Box>
        <Button
          variant="contained"
          color="primary"
          size="large"
          sx={{ borderRadius: 3 }}
          onClick={() => handleActionRequired({ agent: 'Aether', task: 'Schedule a Sales Meeting', status: 'Action Required', intention: 'High-Cost' })}
        >
          Simulate Permission
        </Button>
      </Box>

      {/* Compact Top Stats Row */}
      <Grid container spacing={2} sx={{ flexShrink: 0 }}>
        {/* Carbon Saved — compact horizontal card */}
        <Grid item xs={12} md={6}>
          <Card sx={{
            background: 'linear-gradient(135deg, rgba(46, 125, 50, 0.08) 0%, rgba(255,255,255,0.65) 100%)',
          }}>
            <CardContent sx={{ display: 'flex', alignItems: 'center', gap: 2.5, py: '14px !important', px: 3 }}>
              <Box sx={{
                width: 46, height: 46, borderRadius: 2,
                background: 'linear-gradient(135deg, #2E7D32, #1B5E20)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                boxShadow: '0 4px 14px rgba(46,125,50,0.35)',
                flexShrink: 0
              }}>
                <Co2Icon sx={{ color: '#fff', fontSize: 24 }} />
              </Box>
              <Box>
                <Typography variant="overline" sx={{ fontWeight: 800, color: 'primary.main', display: 'block', lineHeight: 1.3, fontSize: '0.62rem' }}>
                  Total Efficiency
                </Typography>
                <Typography variant="h5" sx={{ fontWeight: 900, color: 'primary.dark', letterSpacing: '-0.03em', lineHeight: 1.1 }}>
                  {gridHealth.carbonSaved.toLocaleString()}
                </Typography>
                <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600 }}>
                  Carbon Saved (kg)
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Grid Health — compact with mini gauge */}
        <Grid item xs={12} md={6}>
          <Card sx={{
            background: 'linear-gradient(135deg, rgba(25, 118, 210, 0.08) 0%, rgba(255,255,255,0.65) 100%)',
          }}>
            <CardContent sx={{ display: 'flex', alignItems: 'center', gap: 2.5, py: '14px !important', px: 3 }}>
              <Box sx={{
                width: 46, height: 46, borderRadius: 2,
                background: 'linear-gradient(135deg, #1976D2, #0D47A1)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                boxShadow: '0 4px 14px rgba(25,118,210,0.35)',
                flexShrink: 0
              }}>
                <BoltIcon sx={{ color: '#fff', fontSize: 24 }} />
              </Box>
              <Box sx={{ flex: 1 }}>
                <Tooltip title="Current Carbon Intensity vs Baseline">
                  <Typography variant="overline" sx={{ fontWeight: 800, color: 'secondary.main', display: 'block', lineHeight: 1.3, fontSize: '0.62rem', cursor: 'help' }}>
                    Current Grid Health
                  </Typography>
                </Tooltip>
                <Typography variant="h5" sx={{ fontWeight: 900, color: isHealthy ? 'success.main' : 'error.main', letterSpacing: '-0.03em', lineHeight: 1.1 }}>
                  {gridHealth.healthScore}%
                </Typography>
                <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600 }}>
                  {isHealthy ? 'Optimal Performance' : 'Needs Attention'}
                </Typography>
              </Box>
              <Box sx={{ width: 72, height: 56, flexShrink: 0 }}>
                <Gauge
                  value={gridHealth.healthScore}
                  startAngle={-110}
                  endAngle={110}
                  innerRadius="75%"
                  outerRadius="100%"
                  sx={{
                    [`& .${gaugeClasses.valueArc}`]: {
                      fill: isHealthy ? '#2E7D32' : '#D32F2F',
                      filter: 'drop-shadow(0px 0px 6px rgba(46, 125, 50, 0.4))',
                    },
                    [`& .${gaugeClasses.valueText}`]: { display: 'none' }
                  }}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Priority: Aether Flow — fills ALL remaining space */}
      <Card sx={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden', minHeight: 0 }}>
        <Box sx={{
          px: 3, py: 2,
          borderBottom: '1px solid rgba(255, 255, 255, 0.4)',
          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
          flexShrink: 0,
        }}>
          <Box>
            <Typography variant="h6" sx={{ fontWeight: 800, color: 'text.primary', letterSpacing: '-0.01em' }}>
              Aether Flow (Active Threads)
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Real-time AI agent orchestration pipeline
            </Typography>
          </Box>
          <Chip
            label="LIVE SYNC ACTIVE"
            size="small"
            sx={{
              fontWeight: 800,
              fontSize: '0.62rem',
              borderRadius: 2,
              background: 'linear-gradient(135deg, #2E7D32, #1B5E20)',
              color: '#fff',
              boxShadow: '0 2px 8px rgba(46,125,50,0.3)',
            }}
          />
        </Box>

        <Box sx={{ flex: 1, overflowY: 'auto', px: 3, py: 2 }}>
          <AgentTimeline onAction={handleActionRequired} />
        </Box>
      </Card>

      {selectedTask && (
        <PermissionDialog
          open={dialogOpen}
          onClose={() => setDialogOpen(false)}
          task={selectedTask}
          gridStatus={gridHealth.status}
        />
      )}
    </Box>
  );
}
