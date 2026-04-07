import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { gridHealthData } from '../mockData';

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
  const [activityLogs, setActivityLogs] = useState([]);
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

  const fetchActivityLogs = async () => {
    try {
      const res = await axios.get('http://localhost:8000/api/activity/logs?limit=10');
      setActivityLogs(res.data);
    } catch (err) {
      console.error("Error fetching activity logs", err);
    }
  };

  useEffect(() => {
    fetchInventory();
    fetchActivityLogs();
  }, []);

  useInterval(() => {
    fetchInventory();
  }, 60000); // Poll inventory every 15 seconds

  useInterval(() => {
    fetchActivityLogs();
  }, 10000); // Poll activity logs every 10 seconds

  return { gridHealth, inventory, activityLogs, loading, fetchInventory };
}
