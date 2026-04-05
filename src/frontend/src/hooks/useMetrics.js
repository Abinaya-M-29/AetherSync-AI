import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { gridHealthData, inventoryData } from '../mockData';

// Custom hook for polling mechanism
function useInterval(callback, delay) {
  const savedCallback = useRef();

  useEffect(() => {
    savedCallback.current = callback;
  }, [callback]);

  useEffect(() => {
    function tick() {
      if (savedCallback.current) {
        savedCallback.current();
      }
    }
    if (delay !== null) {
      const id = setInterval(tick, delay);
      return () => clearInterval(id);
    }
  }, [delay]);
}

export function useMetrics() {
  const [gridHealth, setGridHealth] = useState(gridHealthData);
  const [inventory, setInventory] = useState(inventoryData);
  const [loading, setLoading] = useState(false);

  useInterval(async () => {
    // In a real app, these would hit /api/inventory and /api/grid-status
    // try {
    //   setLoading(true);
    //   const [gridRes, invRes] = await Promise.all([
    //     axios.get('/api/grid-status'),
    //     axios.get('/api/inventory')
    //   ]);
    //   setGridHealth(gridRes.data);
    //   setInventory(invRes.data);
    // } catch (err) {
    //   console.error("Error fetching metrics", err);
    // } finally {
    //   setLoading(false);
    // }

    // Simulating updates for the prototype
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
    }, 500);
  }, 10000); // 10 seconds

  return { gridHealth, inventory, loading };
}
