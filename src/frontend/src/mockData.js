export const inventoryData = [
  { id: 1, itemName: 'Solar Panels (Type 4)', stock: 50, location: 'Warehouse A', status: 'Optimal' },
  { id: 2, itemName: 'Lithium-Ion Batteries', stock: 4, location: 'Warehouse B', status: 'Low' },
  { id: 3, itemName: 'Smart Grid Sensors', stock: 120, location: 'Warehouse A', status: 'Optimal' },
  { id: 4, itemName: 'Inverters (Grid-Tie)', stock: 2, location: 'Warehouse C', status: 'Critical' },
  { id: 5, itemName: 'Cooling Modules', stock: 35, location: 'Warehouse B', status: 'Optimal' },
  { id: 6, itemName: 'High-Voltage Cables (km)', stock: 15, location: 'Warehouse C', status: 'Medium' },
];

export const gridHealthData = {
  healthScore: 88,
  carbonSaved: 12450.5,
  status: 'GREEN'
};

export const agentTasksData = [
  { id: 1, agent: 'Sustainability Agent', task: 'Waiting for Solar Peak', status: 'Thinking', time: '10:05 AM' },
  { id: 2, agent: 'Inventory Agent', task: 'Reordering Inverters', status: 'Action Required', time: '10:12 AM' },
  { id: 3, agent: 'Grid Sync Agent', task: 'Load Balancing Sector 7', status: 'Completed', time: '09:45 AM' },
];

// 24 Hour simulated energy intensity (Chennai Power Grid)
const generateChartData = () => {
  const data = [];
  let intensity = 400; // Baseline
  for (let i = 0; i < 24; i++) {
    // Dip during day (solar), spike in evening
    if (i >= 8 && i <= 16) {
      intensity = 200 + Math.random() * 50; // Solar peak
    } else if (i >= 18 && i <= 22) {
      intensity = 500 + Math.random() * 100; // Evening peak
    } else {
      intensity = 350 + Math.random() * 50; // Night/Morning
    }
    
    data.push({
      time: `${i.toString().padStart(2, '0')}:00`,
      intensity: Math.round(intensity)
    });
  }
  return data;
};

export const sustainabilityChartData = generateChartData();
