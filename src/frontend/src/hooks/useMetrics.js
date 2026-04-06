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
  const [inventory, setInventory] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchInventory = async () => {
    try {
      setLoading(true);
      const invRes = await axios.get('http://localhost:8000/api/inventory/products');
      setInventory(invRes.data);
    } catch (err) {
      console.error("Error fetching inventory", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInventory();
  }, []);

  useInterval(() => {
    fetchInventory();
  }, 15000); // Poll every 15 seconds

  return { gridHealth, inventory, loading, fetchInventory };
}
