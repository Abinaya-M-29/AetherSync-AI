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
  const [feedbackSummary, setFeedbackSummary] = useState({ average_rating: 0, total_reviews: 0, out_of: 5 });
  const [loading, setLoading] = useState(true);

  const fetchInventory = async () => {
    try {
      setLoading(true);
      const invRes = await axios.get('/api/inventory/products');
      setInventory(invRes.data);
    } catch (err) {
      console.error("Error fetching inventory", err);
    } finally {
      setLoading(false);
    }
  };

  const fetchActivityLogs = async () => {
    try {
      const res = await axios.get('/api/activity/logs?limit=10');
      setActivityLogs(res.data);
    } catch (err) {
      console.error("Error fetching activity logs", err);
    }
  };

  const fetchFeedbackSummary = async () => {
    try {
      const res = await axios.get('/api/feedback/summary');
      setFeedbackSummary(res.data);
    } catch (err) {
      console.error("Error fetching feedback summary", err);
    }
  };

  useEffect(() => {
    fetchInventory();
    fetchActivityLogs();
    fetchFeedbackSummary();
  }, []);

  useInterval(() => {
    fetchInventory();
  }, 60000); // Poll inventory every 60 seconds

  useInterval(() => {
    fetchActivityLogs();
  }, 10000); // Poll activity logs every 10 seconds

  useInterval(() => {
    fetchFeedbackSummary();
  }, 15000); // Poll feedback summary every 15 seconds

  return { gridHealth, inventory, activityLogs, feedbackSummary, loading, fetchInventory };
}
