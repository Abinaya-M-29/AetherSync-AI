import { useState } from 'react';
import { Box, Typography, Button, Card, Dialog, DialogTitle, DialogContent, DialogActions, TextField, Chip, LinearProgress } from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import axios from 'axios';
import { useMetrics } from '../../hooks/useMetrics';

export default function Inventory() {
  const { inventory, loading, fetchInventory } = useMetrics();

  const [sellModalOpen, setSellModalOpen] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [sellQuantity, setSellQuantity] = useState(1);

  const handleSellClick = (product) => {
    setSelectedProduct(product);
    setSellQuantity(1);
    setSellModalOpen(true);
  };

  const handleSellSubmit = async () => {
    if (!selectedProduct || sellQuantity <= 0) return;

    // Remove focus from the active element (e.g. the Confirm button) to prevent 
    // the "Blocked aria-hidden on an element because its descendant retained focus" warning.
    if (document.activeElement && document.activeElement instanceof HTMLElement) {
      document.activeElement.blur();
    }

    try {
      const res = await axios.post(`/api/inventory/products/${selectedProduct.sku}/sell`, {
        quantity: parseInt(sellQuantity, 10)
      });
      setSellModalOpen(false);
      fetchInventory(); // Refresh the grid

      if (res.data.agent_triggered) {
        alert(`${res.data.message}\n\n🤖 AetherSync AI Triggered!\nStock is now low. Auto-restock workflow initiated (actions may be queued depending on Carbon Hours). Check Activity Logs!`);
      } else {
        alert(res.data.message);
      }
    } catch (error) {
      console.error("Error selling product:", error);
      alert(error.response?.data?.detail || "Failed to sell product");
    }
  };

  const columns = [
    { field: 'sku', headerName: 'SKU', width: 100 },
    { field: 'itemName', headerName: 'Item Name', flex: 1 },
    { field: 'location', headerName: 'Category', flex: 1 },
    {
      field: 'stock',
      headerName: 'Stock Level',
      width: 100,
      type: 'number'
    },
    {
      field: 'status',
      headerName: 'Status',
      width: 140,
      renderCell: (params) => {
        let gradient = 'none';
        let color = '#fff';

        if (params.value === "Low") {
          gradient = 'linear-gradient(135deg, #ff0844 0%, #ffb199 100%)';
        } else if (params.value === "Medium") {
          gradient = 'linear-gradient(135deg, #f6d365 0%, #fda085 100%)';
          color = '#000'; // dark text for readability on yellow
        } else if (params.value === "High") {
          gradient = 'linear-gradient(135deg, #a8e063 0%, #56ab2f 100%)';
        } else if (params.value === "Out of Stock") {
          gradient = 'linear-gradient(135deg, #434343 0%, #000000 100%)';
        }

        return (
          <Chip
            label={params.value}
            size="small"
            sx={{
              background: gradient,
              color: color,
              fontWeight: 'bold',
              border: 'none',
              boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
            }}
          />
        );
      }
    },
    {
      field: 'action',
      headerName: 'Action',
      sortable: false,
      flex: 1,
      minWidth: 160,
      renderCell: (params) => {
        return (
          <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
            <Button
              variant="contained"
              size="small"
              color="primary"
              disabled={params.row.stock <= 0}
              onClick={() => handleSellClick(params.row)}
            >
              Sell
            </Button>
            {params.row.stock <= params.row.reorder_level && (
              <Button
                variant="outlined"
                size="small"
                color="secondary"
              >
                Reorder
              </Button>
            )}
          </Box>
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
          slots={{ loadingOverlay: LinearProgress }}
          initialState={{
            pagination: {
              paginationModel: { page: 0, pageSize: 10 },
            },
          }}
          pageSizeOptions={[5, 10]}
          disableRowSelectionOnClick
          getRowClassName={(params) =>
            params.row.stock <= params.row.reorder_level ? 'super-app-theme--LowStock' : ''
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

      <Dialog
        open={sellModalOpen}
        onClose={() => setSellModalOpen(false)}
        PaperProps={{
          sx: {
            backgroundColor: '#ffffff',
            color: '#000000',
            borderRadius: '12px',
          }
        }}
      >
        <DialogTitle sx={{ color: '#000' }}>Sell Product</DialogTitle>
        <DialogContent>
          <Typography variant="body1" sx={{ mb: 2, color: '#333' }}>
            Selling: {selectedProduct?.itemName} (Available: {selectedProduct?.stock})
          </Typography>
          <TextField
            autoFocus
            margin="dense"
            label="Quantity"
            type="number"
            fullWidth
            variant="outlined"
            value={sellQuantity}
            onChange={(e) => setSellQuantity(e.target.value)}
            inputProps={{ min: 1, max: selectedProduct?.stock || 1 }}
            sx={{
              '& .MuiOutlinedInput-root': {
                color: '#000',
                '& fieldset': { borderColor: 'rgba(0,0,0,0.2)' },
                '&:hover fieldset': { borderColor: 'rgba(0,0,0,0.4)' },
              },
              '& .MuiInputLabel-root': { color: '#666' },
            }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSellModalOpen(false)} sx={{ color: '#666' }}>Cancel</Button>
          <Button onClick={handleSellSubmit} variant="contained" color="primary">
            Confirm Sale
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
