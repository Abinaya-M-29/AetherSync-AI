import { Box, Card, CardContent, Typography, Button, Grid, Tooltip, Chip, Snackbar, Alert, CircularProgress } from '@mui/material';
import { useMetrics } from '../../hooks/useMetrics';
import AgentTimeline from '../AgentTimeline';
import PermissionDialog from '../PermissionDialog';
import { useState } from 'react';
import { Gauge, gaugeClasses } from '@mui/x-charts/Gauge';
import Co2Icon from '@mui/icons-material/Co2';
import BoltIcon from '@mui/icons-material/Bolt';
import StarIcon from '@mui/icons-material/Star';
import InventoryIcon from '@mui/icons-material/Inventory2';
import RequestQuoteIcon from '@mui/icons-material/RequestQuote';
import FeedbackIcon from '@mui/icons-material/Feedback';
import axios from 'axios';

export default function Dashboard() {
  const { gridHealth, activityLogs, feedbackSummary } = useMetrics();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [selectedTask, setSelectedTask] = useState(null);
  const [agentLoading, setAgentLoading] = useState({ inventory: false, quotation: false, feedback: false });
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

  const handleActionRequired = (task) => {
    setSelectedTask(task);
    setDialogOpen(true);
  };

  const isHealthy = gridHealth.status === 'GREEN';

  const triggerAgent = async (agentKey, endpoint, label) => {
    setAgentLoading(prev => ({ ...prev, [agentKey]: true }));
    try {
      await axios.post(endpoint);
      setSnackbar({ open: true, message: `${label} triggered! Watch the Aether Flow for live updates.`, severity: 'success' });
    } catch (err) {
      setSnackbar({ open: true, message: `Failed to trigger ${label}. Please try again.`, severity: 'error' });
    } finally {
      setAgentLoading(prev => ({ ...prev, [agentKey]: false }));
    }
  };

  const agentActions = [
    {
      key: 'inventory',
      label: 'Inventory Check',
      description: 'Scan stock & alert suppliers',
      endpoint: '/check-inventory',
      icon: <InventoryIcon />,
      gradient: 'linear-gradient(135deg, #2E7D32, #1B5E20)',
      shadow: 'rgba(46,125,50,0.35)',
    },
    {
      key: 'quotation',
      label: 'Quotation Agent',
      description: 'Reply to "Quotation for ..." emails',
      endpoint: '/automated_quotation_agent',
      icon: <RequestQuoteIcon />,
      gradient: 'linear-gradient(135deg, #1565C0, #0D47A1)',
      shadow: 'rgba(21,101,192,0.35)',
    },
    {
      key: 'feedback',
      label: 'Feedback Agent',
      description: 'Process "Feedback on ..." emails',
      endpoint: '/automated_feedback_agent',
      icon: <FeedbackIcon />,
      gradient: 'linear-gradient(135deg, #6A1B9A, #4A148C)',
      shadow: 'rgba(106,27,154,0.35)',
    },
  ];

  const ratingStars = (rating) => {
    const full = Math.round(rating);
    return Array.from({ length: 5 }, (_, i) => (
      <StarIcon key={i} sx={{ fontSize: 16, color: i < full ? '#F9A825' : 'rgba(0,0,0,0.15)' }} />
    ));
  };

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
        {/* Carbon Saved */}
        <Grid item xs={12} md={4}>
          <Card sx={{ background: 'linear-gradient(135deg, rgba(46, 125, 50, 0.08) 0%, rgba(255,255,255,0.65) 100%)' }}>
            <CardContent sx={{ display: 'flex', alignItems: 'center', gap: 2.5, py: '14px !important', px: 3 }}>
              <Box sx={{
                width: 46, height: 46, borderRadius: 2,
                background: 'linear-gradient(135deg, #2E7D32, #1B5E20)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                boxShadow: '0 4px 14px rgba(46,125,50,0.35)', flexShrink: 0
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

        {/* Grid Health */}
        <Grid item xs={12} md={4}>
          <Card sx={{ background: 'linear-gradient(135deg, rgba(25, 118, 210, 0.08) 0%, rgba(255,255,255,0.65) 100%)' }}>
            <CardContent sx={{ display: 'flex', alignItems: 'center', gap: 2.5, py: '14px !important', px: 3 }}>
              <Box sx={{
                width: 46, height: 46, borderRadius: 2,
                background: 'linear-gradient(135deg, #1976D2, #0D47A1)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                boxShadow: '0 4px 14px rgba(25,118,210,0.35)', flexShrink: 0
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

        {/* Feedback Rating Card */}
        <Grid item xs={12} md={4}>
          <Card sx={{ background: 'linear-gradient(135deg, rgba(106,27,154,0.08) 0%, rgba(255,255,255,0.65) 100%)' }}>
            <CardContent sx={{ display: 'flex', alignItems: 'center', gap: 2.5, py: '14px !important', px: 3 }}>
              <Box sx={{
                width: 46, height: 46, borderRadius: 2,
                background: 'linear-gradient(135deg, #6A1B9A, #4A148C)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                boxShadow: '0 4px 14px rgba(106,27,154,0.35)', flexShrink: 0
              }}>
                <StarIcon sx={{ color: '#fff', fontSize: 24 }} />
              </Box>
              <Box>
                <Typography variant="overline" sx={{ fontWeight: 800, color: '#6A1B9A', display: 'block', lineHeight: 1.3, fontSize: '0.62rem' }}>
                  Overall Feedback
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'baseline', gap: 0.5 }}>
                  <Typography variant="h5" sx={{ fontWeight: 900, color: '#4A148C', letterSpacing: '-0.03em', lineHeight: 1.1 }}>
                    {feedbackSummary.average_rating > 0 ? feedbackSummary.average_rating : '—'}
                  </Typography>
                  {feedbackSummary.average_rating > 0 && (
                    <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 700 }}>/5</Typography>
                  )}
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  {feedbackSummary.average_rating > 0 ? ratingStars(feedbackSummary.average_rating) : null}
                  <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600, ml: 0.5 }}>
                    {feedbackSummary.total_reviews > 0 ? `${feedbackSummary.total_reviews} review${feedbackSummary.total_reviews > 1 ? 's' : ''}` : 'No reviews yet'}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Agent Action Buttons */}
      <Card sx={{ flexShrink: 0, p: 0 }}>
        <Box sx={{ px: 3, pt: 2, pb: 1 }}>
          <Typography variant="overline" sx={{ fontWeight: 800, color: 'text.secondary', fontSize: '0.65rem', letterSpacing: '0.1em' }}>
            Manual Agent Triggers
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 2, px: 3, pb: 2, flexWrap: 'wrap' }}>
          {agentActions.map((action) => (
            <Button
              key={action.key}
              id={`trigger-${action.key}-agent`}
              variant="contained"
              size="medium"
              disabled={agentLoading[action.key]}
              startIcon={agentLoading[action.key] ? <CircularProgress size={16} sx={{ color: 'white' }} /> : action.icon}
              onClick={() => triggerAgent(action.key, action.endpoint, action.label)}
              sx={{
                background: agentLoading[action.key] ? 'rgba(0,0,0,0.2)' : action.gradient,
                boxShadow: `0 4px 14px ${action.shadow}`,
                borderRadius: 2.5,
                px: 2.5,
                py: 1,
                fontWeight: 700,
                fontSize: '0.82rem',
                textTransform: 'none',
                transition: 'all 0.25s ease',
                '&:hover': {
                  opacity: 0.88,
                  transform: 'translateY(-1px)',
                  boxShadow: `0 6px 20px ${action.shadow}`,
                },
              }}
            >
              <Box>
                <Box>{action.label}</Box>
                <Typography variant="caption" sx={{ opacity: 0.8, display: 'block', lineHeight: 1.1, fontWeight: 500, fontSize: '0.67rem' }}>
                  {action.description}
                </Typography>
              </Box>
            </Button>
          ))}
        </Box>
      </Card>

      {/* Aether Flow — fills ALL remaining space */}
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
          <AgentTimeline tasks={activityLogs} onAction={handleActionRequired} />
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

      {/* Snackbar Notification */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={5000}
        onClose={() => setSnackbar(prev => ({ ...prev, open: false }))}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert
          onClose={() => setSnackbar(prev => ({ ...prev, open: false }))}
          severity={snackbar.severity}
          variant="filled"
          sx={{ fontWeight: 700 }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
}

