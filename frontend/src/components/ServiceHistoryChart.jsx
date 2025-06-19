import React from 'react'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'
import { Line as LineChart } from 'react-chartjs-2'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  Chip
} from '@mui/material'
import { Close as CloseIcon } from '@mui/icons-material'

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

const ServiceHistoryChart = ({ open, onClose, serviceName, historyData }) => {
  if (!historyData || historyData.length === 0) {
    return (
      <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
        <DialogTitle>
          <Typography variant="h6">Service History - {serviceName}</Typography>
        </DialogTitle>
        <DialogContent>
          <Typography variant="body1" textAlign="center" py={4}>
            No historical data available for this service.
          </Typography>
        </DialogContent>
      </Dialog>
    )
  }

  // Process data for the chart
  const processedData = historyData
    .filter(item => item.name === serviceName)
    .sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp))
    .slice(-50) // Show last 50 data points

  const labels = processedData.map(item => {
    const date = new Date(item.timestamp)
    return date.toLocaleTimeString()
  })

  const responseTimes = processedData.map(item => item.response_time || 0)
  const statusData = processedData.map(item => item.status === 'up' ? 1 : 0)

  const chartData = {
    labels,
    datasets: [
      {
        label: 'Response Time (ms)',
        data: responseTimes,
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        yAxisID: 'y',
        fill: false,
        tension: 0.1
      },
      {
        label: 'Status (1=Up, 0=Down)',
        data: statusData,
        borderColor: 'rgb(255, 99, 132)',
        backgroundColor: 'rgba(255, 99, 132, 0.2)',
        yAxisID: 'y1',
        fill: false,
        tension: 0.1,
        pointRadius: 4
      }
    ]
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index',
      intersect: false,
    },
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: `${serviceName} - Last 24 Hours`,
        color: '#ffffff'
      },
    },
    scales: {
      x: {
        display: true,
        title: {
          display: true,
          text: 'Time',
          color: '#ffffff'
        },
        ticks: {
          color: '#ffffff',
          maxTicksLimit: 10
        }
      },
      y: {
        type: 'linear',
        display: true,
        position: 'left',
        title: {
          display: true,
          text: 'Response Time (ms)',
          color: '#ffffff'
        },
        ticks: {
          color: '#ffffff'
        }
      },
      y1: {
        type: 'linear',
        display: true,
        position: 'right',
        title: {
          display: true,
          text: 'Status',
          color: '#ffffff'
        },
        ticks: {
          color: '#ffffff',
          stepSize: 1,
          min: 0,
          max: 1
        },
        grid: {
          drawOnChartArea: false,
        },
      },
    },
  }

  // Calculate statistics
  const upCount = statusData.filter(status => status === 1).length
  const downCount = statusData.filter(status => status === 0).length
  const totalChecks = statusData.length
  const uptimePercentage = totalChecks > 0 ? ((upCount / totalChecks) * 100).toFixed(1) : 0
  const avgResponseTime = responseTimes.length > 0 
    ? (responseTimes.reduce((a, b) => a + b, 0) / responseTimes.length).toFixed(0)
    : 0

  return (
    <Dialog open={open} onClose={onClose} maxWidth="lg" fullWidth>
      <DialogTitle>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="h6">Service History - {serviceName}</Typography>
          <Button onClick={onClose} startIcon={<CloseIcon />}>
            Close
          </Button>
        </Box>
      </DialogTitle>
      <DialogContent>
        <Box mb={3}>
          <Typography variant="h6" gutterBottom>
            Statistics (Last 24 Hours)
          </Typography>
          <Box display="flex" gap={2} flexWrap="wrap">
            <Chip 
              label={`Uptime: ${uptimePercentage}%`} 
              color={uptimePercentage >= 99 ? 'success' : uptimePercentage >= 95 ? 'warning' : 'error'}
            />
            <Chip label={`Total Checks: ${totalChecks}`} variant="outlined" />
            <Chip label={`Up: ${upCount}`} color="success" variant="outlined" />
            <Chip label={`Down: ${downCount}`} color="error" variant="outlined" />
            <Chip label={`Avg Response: ${avgResponseTime}ms`} variant="outlined" />
          </Box>
        </Box>
        
        <Box sx={{ height: 400, width: '100%' }}>
          <LineChart data={chartData} options={options} />
        </Box>
      </DialogContent>
    </Dialog>
  )
}

export default ServiceHistoryChart 