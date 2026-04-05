import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#2E7D32', // Aether Green
      light: '#A5D6A7',
      dark: '#1B5E20',
      contrastText: '#ffffff',
    },
    secondary: {
      main: '#1976D2', // Sync Blue
      light: '#90CAF9',
      dark: '#0D47A1',
      contrastText: '#ffffff',
    },
    background: {
      default: 'rgba(0, 0, 0, 0)', // rgba equivalent of transparent — MUI-safe
      paper: 'rgba(255, 255, 255, 0.7)', // Semi-transparent for glass
    },
    text: {
      primary: '#1A2027',
      secondary: '#454C5E',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", sans-serif',
    h5: {
      fontWeight: 800,
      letterSpacing: '-0.02em',
      color: '#1A2027',
    },
    h6: {
      fontWeight: 700,
      fontSize: '1.2rem',
      letterSpacing: '-0.01em',
    },
    button: {
      textTransform: 'none',
      fontWeight: 700,
      borderRadius: 12,
    },
  },
  shape: {
    borderRadius: 16, // More modern rounded corners
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          padding: '10px 24px',
          transition: 'all 0.2s ease-in-out',
          '&:hover': {
            transform: 'translateY(-2px)',
            boxShadow: '0 8px 16px rgba(46, 125, 50, 0.15)',
          },
        },
        containedPrimary: {
          background: 'linear-gradient(135deg, #2E7D32 0%, #1B5E20 100%)',
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          backdropFilter: 'blur(12px)',
          backgroundColor: 'rgba(255, 255, 255, 0.6)',
          border: '1px solid rgba(255, 255, 255, 0.3)',
          boxShadow: '0 8px 32px 0 rgba(31, 38, 135, 0.07)',
          transition: 'all 0.3s ease-out',
          '&:hover': {
            transform: 'translateY(-4px)',
            boxShadow: '0 12px 40px 0 rgba(31, 38, 135, 0.12)',
            border: '1px solid rgba(255, 255, 255, 0.5)',
          },
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backdropFilter: 'blur(10px)',
          backgroundColor: 'rgba(255, 255, 255, 0.4)',
          color: '#1A2027',
          borderBottom: '1px solid rgba(255, 255, 255, 0.3)',
          boxShadow: 'none',
        },
      },
    },
  },
});

export default theme;
