import { Box, Typography, Button, Card } from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import { useMetrics } from '../../hooks/useMetrics';

export default function Inventory() {
  const { inventory, loading } = useMetrics();

  const columns = [
    { field: 'id', headerName: 'ID', width: 70 },
    { field: 'itemName', headerName: 'Item Name', flex: 1 },
    { field: 'location', headerName: 'Location', flex: 1 },
    {
      field: 'stock',
      headerName: 'Stock Level',
      width: 130,
      type: 'number'
    },
    {
      field: 'status',
      headerName: 'Status',
      width: 130,
    },
    {
      field: 'action',
      headerName: 'Action',
      sortable: false,
      width: 120,
      renderCell: (params) => {
        return (
          <Button
            variant="outlined"
            size="small"
            color="secondary"
            disabled={params.row.stock >= 5}
            sx={{ mt: 1 }}
          >
            Reorder
          </Button>
        );
      }
    }
  ];

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
        Inventory Management
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 4 }}>
        Real-time tracking of hardware and resource stocks
      </Typography>

      <Card sx={{ height: 'calc(100vh - 240px)', width: '100%', p: 0, overflow: 'hidden' }}>
        <DataGrid
          rows={inventory}
          columns={columns}
          loading={loading}
          initialState={{
            pagination: {
              paginationModel: { page: 0, pageSize: 10 },
            },
          }}
          pageSizeOptions={[5, 10]}
          disableRowSelectionOnClick
          getRowClassName={(params) =>
            params.row.stock < 5 ? 'super-app-theme--LowStock' : ''
          }
          sx={{
            border: 0,
            '& .MuiDataGrid-main': {
              backgroundColor: 'rgba(0, 0, 0, 0)',
            },
            '& .MuiDataGrid-columnHeaders': {
              backgroundColor: 'rgba(255, 255, 255, 0.2)',
              borderBottom: '1px solid rgba(255, 255, 255, 0.3)',
            },
            '& .MuiDataGrid-cell': {
              borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
            },
            '& .super-app-theme--LowStock': {
              bgcolor: 'rgba(211, 47, 47, 0.08)',
              '&:hover': {
                bgcolor: 'rgba(211, 47, 47, 0.12)',
              },
            },
          }}
        />
      </Card>
    </Box>
  );
}
