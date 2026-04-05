import { Timeline, TimelineItem, TimelineSeparator, TimelineConnector, TimelineContent, TimelineDot } from '@mui/lab';
import { Typography, Box, Button, Chip } from '@mui/material';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import { agentTasksData } from '../mockData';

export default function AgentTimeline({ onAction }) {
  return (
    <Timeline sx={{ p: 0, m: 0 }}>
      {agentTasksData.map((task, index) => {
        const isLast = index === agentTasksData.length - 1;
        const needsAction = task.status === 'Action Required';
        
        let color = 'primary';
        if (task.status === 'Completed') color = 'success';
        if (needsAction) color = 'warning';

        return (
          <TimelineItem key={task.id} sx={{ minHeight: 60, '&::before': { display: 'none' } }}>
            <TimelineSeparator>
              <TimelineDot color={color} variant={task.status === 'Thinking' ? 'outlined' : 'filled'}>
                <SmartToyIcon fontSize="small" />
              </TimelineDot>
              {!isLast && <TimelineConnector />}
            </TimelineSeparator>
            <TimelineContent sx={{ py: '12px', px: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <Box>
                  <Typography variant="body2" fontWeight="bold" component="span">
                    {task.agent}:
                  </Typography>
                  <Typography variant="body2" color="text.secondary" component="span" sx={{ ml: 1 }}>
                    {task.task}
                  </Typography>
                </Box>
                <Typography variant="caption" color="text.secondary">
                  {task.time}
                </Typography>
              </Box>
              
              <Box sx={{ mt: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
                <Chip 
                  label={task.status} 
                  size="small" 
                  color={color} 
                  variant={needsAction ? 'filled' : 'outlined'}
                  sx={{ height: 20, fontSize: '0.7rem' }}
                />
                {needsAction && (
                  <Button 
                    size="small" 
                    color="warning" 
                    variant="text" 
                    sx={{ p: 0, minWidth: 'auto', fontSize: '0.75rem', ml: 1 }}
                    onClick={() => onAction(task)}
                  >
                    View Details
                  </Button>
                )}
              </Box>
            </TimelineContent>
          </TimelineItem>
        );
      })}
    </Timeline>
  );
}
