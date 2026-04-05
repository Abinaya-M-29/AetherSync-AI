import { Box, Typography, Card, CardContent } from '@mui/material';
import { LineChart } from '@mui/x-charts/LineChart';
import { sustainabilityChartData } from '../../mockData';

export default function Sustainability() {
  return (
    <Box sx={{ p: 1 }}>
      <Typography variant="h4" sx={{ 
        fontWeight: 900, 
        letterSpacing: '-0.04em',
        mb: 1,
        background: 'linear-gradient(45deg, #1A2027 30%, #454C5E 90%)',
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent',
      }}>
        Grid Sustainability & Intensity
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 4 }}>
        Predictive analysis of carbon footprint and renewable energy mix
      </Typography>
      
      <Card sx={{ p: 3, background: 'rgba(255, 255, 255, 0.4)', border: '1px solid rgba(255, 255, 255, 0.3)' }}>
        <CardContent>
          <Typography variant="h6" color="text.primary" sx={{ fontWeight: 800, mb: 1 }}>
            Chennai Power Grid - Simulated Energy Intensity (24h)
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 5 }}>
            Lower intensity represents cleaner power (high solar/wind utilization). High intensity indicates reliance on fossil fuels.
          </Typography>

          <Box sx={{ width: '100%', height: 420 }}>
            <LineChart
              dataset={sustainabilityChartData}
              xAxis={[{ 
                dataKey: 'time', 
                scaleType: 'point',
                label: 'Time of Day',
              }]}
              series={[{ 
                dataKey: 'intensity', 
                area: true, 
                color: '#2E7D32',
                label: 'Carbon Intensity (gCO2/kWh)',
                showMark: false,
              }]}
              sx={{
                '& .MuiAreaElement-root': {
                   fill: 'url(#gradient-green)',
                   fillOpacity: 0.3,
                },
                '& .MuiLineElement-root': {
                  strokeWidth: 3,
                },
              }}
              margin={{ top: 20, bottom: 60, left: 70, right: 30 }}
            />
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
}
