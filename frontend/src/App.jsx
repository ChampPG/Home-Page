import { useState, useEffect } from 'react'
import {
  ThemeProvider,
  createTheme,
  CssBaseline,
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Grid,
  Chip,
  CircularProgress,
  Alert,
  Button,
  AppBar,
  Toolbar,
  Paper,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip as MuiChip
} from '@mui/material'
import {
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Refresh as RefreshIcon,
  Schedule as ScheduleIcon,
  AccessTime as AccessTimeIcon,
  TrendingUp as TrendingUpIcon,
  Launch as LaunchIcon,
  Link as LinkIcon,
  History as HistoryIcon,
  Computer as ComputerIcon
} from '@mui/icons-material'
import ServiceHistoryChart from './components/ServiceHistoryChart'

// Import logo
import logoLarge from '/assets/logo-large.svg'
import logo from '/assets/logo.svg'

// Create dark theme
const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#89b4fa', // Blue
    },
    secondary: {
      main: '#cba6f7', // Mauve
    },
    background: {
      default: '#1e1e2e', // Base
      paper: '#313244', // Surface0
    },
    success: {
      main: '#a6e3a1', // Green
    },
    error: {
      main: '#f38ba8', // Red
    },
    warning: {
      main: '#f9e2af', // Yellow
    },
    info: {
      main: '#89dceb', // Sky
    },
    text: {
      primary: '#cdd6f4', // Text
      secondary: '#bac2de', // Subtext1
    },
    divider: '#45475a', // Surface1
  },
  typography: {
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", "Oxygen", "Ubuntu", "Cantarell", "Fira Sans", "Droid Sans", "Helvetica Neue", sans-serif',
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          transition: 'all 0.3s ease',
          backgroundColor: '#313244', // Surface0
          border: '1px solid #45475a', // Surface1
          '&:hover': {
            transform: 'translateY(-2px)',
            boxShadow: '0 8px 25px -8px rgba(0, 0, 0, 0.3)',
            backgroundColor: '#45475a', // Surface1
          },
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: '#181825', // Mantle
          borderBottom: '1px solid #45475a', // Surface1
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          backgroundColor: '#45475a', // Surface1
          color: '#cdd6f4', // Text
          '&.MuiChip-colorSuccess': {
            backgroundColor: '#a6e3a1', // Green
            color: '#1e1e2e', // Base
          },
          '&.MuiChip-colorError': {
            backgroundColor: '#f38ba8', // Red
            color: '#1e1e2e', // Base
          },
          '&.MuiChip-colorPrimary': {
            backgroundColor: '#89b4fa', // Blue
            color: '#1e1e2e', // Base
          },
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          '&.MuiButton-outlined': {
            borderColor: '#6c7086', // Overlay0
            color: '#cdd6f4', // Text
            '&:hover': {
              borderColor: '#89b4fa', // Blue
              backgroundColor: 'rgba(137, 180, 250, 0.08)', // Blue with opacity
            },
          },
          '&.MuiButton-text': {
            color: '#cdd6f4', // Text
            '&:hover': {
              backgroundColor: 'rgba(205, 214, 244, 0.08)', // Text with opacity
            },
          },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundColor: '#313244', // Surface0
          border: '1px solid #45475a', // Surface1
        },
      },
    },
    MuiDivider: {
      styleOverrides: {
        root: {
          borderColor: '#45475a', // Surface1
        },
      },
    },
    MuiAlert: {
      styleOverrides: {
        root: {
          backgroundColor: '#313244', // Surface0
          border: '1px solid #45475a', // Surface1
        },
      },
    },
  },
})

function App() {
  const [services, setServices] = useState([])
  const [downtimeEvents, setDowntimeEvents] = useState([])
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [historyData, setHistoryData] = useState([])
  const [historyChartOpen, setHistoryChartOpen] = useState(false)
  const [selectedService, setSelectedService] = useState(null)
  const [checkInterval, setCheckInterval] = useState(null)

  useEffect(() => {
    fetchServices()
    fetchHistoryData()
    // Refresh every 30 seconds
    const interval = setInterval(() => {
      fetchServices()
      fetchHistoryData()
    }, 30000)
    return () => clearInterval(interval)
  }, [])

  const fetchServices = async () => {
    try {
      const response = await fetch('/api/v1/services')
      if (!response.ok) {
        throw new Error('Failed to fetch services')
      }
      const data = await response.json()
      setServices(data.services || [])
      setDowntimeEvents(data.downtime_events || [])
      setCategories(data.categories || [])
      setCheckInterval(data.interval || null)
      setLoading(false)
    } catch (err) {
      setError(err.message)
      setLoading(false)
    }
  }

  const fetchHistoryData = async () => {
    try {
      const response = await fetch('/api/v1/services/history')
      if (!response.ok) {
        throw new Error('Failed to fetch history data')
      }
      const data = await response.json()
      setHistoryData(data.history || [])
    } catch (err) {
      console.error('Error fetching history data:', err)
    }
  }

  const handleHistoryClick = (serviceName) => {
    setSelectedService(serviceName)
    setHistoryChartOpen(true)
  }

  // Group services by category and get latest status for each service
  const getServicesByCategory = () => {
    const latestServices = {}
    
    // Get the latest status for each service
    services.forEach(service => {
      if (!latestServices[service.name] || new Date(service.timestamp) > new Date(latestServices[service.name].timestamp)) {
        latestServices[service.name] = service
      }
    })

    // Group by category in the order specified in config
    const groupedServices = {}
    categories.forEach(category => {
      groupedServices[category] = []
    })

    Object.values(latestServices).forEach(service => {
      if (groupedServices[service.category]) {
        groupedServices[service.category].push(service)
      }
    })

    return groupedServices
  }

  // Group services by hosts
  const getServicesByHosts = () => {
    // console.log('All services:', services)
    
    // Get the latest status for each service to avoid duplicates
    const latestServices = {}
    services.forEach(service => {
      if (!latestServices[service.name] || 
          (service.timestamp && latestServices[service.name].timestamp && 
           new Date(service.timestamp) > new Date(latestServices[service.name].timestamp))) {
        latestServices[service.name] = service
      }
    })
    
    // Separate hosts, redirects, and other services
    const hosts = {}
    const redirects = []
    const otherServices = []
    const servicesWithHosts = [] // New array to collect services with host fields

    // Process all services from the API data
    Object.values(latestServices).forEach(service => {
      // console.log('Processing service:', service.name, 'type:', service.type, 'host:', service.host)
      
      if (service.type === 'host') {
        hosts[service.ping_url] = {
          ...service,
          instances: []
        }
        // console.log('Added host:', service.name, 'with ping_url:', service.ping_url)
      } else if (service.type === 'redirect') {
        redirects.push(service)
      } else if (service.host) {
        // Collect services with host fields for later mapping
        servicesWithHosts.push(service)
        // console.log('Added service with host:', service.name, 'host:', service.host)
      } else {
        // Only add to otherServices if they don't have a host field
        otherServices.push(service)
      }
    })

    // console.log('Hosts found:', Object.keys(hosts))
    // console.log('Other services:', otherServices.map(s => ({ name: s.name, host: s.host })))

    // Group instances under their hosts
    servicesWithHosts.forEach(service => {
      if (service.host && hosts[service.host]) {
        hosts[service.host].instances.push(service)
        // console.log('Mapped service', service.name, 'to host', service.host)
      } else if (service.host) {
        // console.log('Could not find host for service:', service.name, 'looking for host:', service.host)
      }
    })

    // Sort instances by category within each host
    Object.values(hosts).forEach(host => {
      host.instances.sort((a, b) => {
        const categoryOrder = categories.indexOf(a.category) - categories.indexOf(b.category)
        if (categoryOrder !== 0) {
          return categoryOrder
        }
        // If same category, sort by name
        return a.name.localeCompare(b.name)
      })
    })

    // Sort redirects by category
    redirects.sort((a, b) => {
      const categoryOrder = categories.indexOf(a.category) - categories.indexOf(b.category)
      if (categoryOrder !== 0) {
        return categoryOrder
      }
      // If same category, sort by name
      return a.name.localeCompare(b.name)
    })

    // console.log('Final result:', { hosts: Object.keys(hosts), redirects: redirects.length, otherServices: otherServices.length })
    return { hosts, redirects, otherServices }
  }

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString()
  }

  const formatDuration = (timestamp) => {
    if (!timestamp) return 'Unknown'
    
    const now = new Date()
    const checkTime = new Date(timestamp)
    const diffMs = now - checkTime
    const diffSeconds = Math.floor(diffMs / 1000)
    const diffMinutes = Math.floor(diffSeconds / 60)
    const diffHours = Math.floor(diffMinutes / 60)
    const diffDays = Math.floor(diffHours / 24)
    
    if (diffDays > 0) {
      return `${diffDays}d ${diffHours % 24}h ${diffMinutes % 60}m`
    } else if (diffHours > 0) {
      return `${diffHours}h ${diffMinutes % 60}m`
    } else if (diffMinutes > 0) {
      return `${diffMinutes}m ${diffSeconds % 60}s`
    } else {
      return `${diffSeconds}s`
    }
  }

  const getStatusIcon = (status) => {
    if (status === 'redirect') return <LinkIcon color="primary" />
    return status === 'up' ? <CheckCircleIcon color="success" /> : <ErrorIcon color="error" />
  }

  const getStatusColor = (status) => {
    if (status === 'redirect') return 'primary'
    return status === 'up' ? 'success' : 'error'
  }

  const formatCategoryName = (category) => {
    return category.charAt(0).toUpperCase() + category.slice(1)
  }

  const formatInterval = (seconds) => {
    if (seconds < 60) {
      return `${seconds} second${seconds !== 1 ? 's' : ''}`
    } else if (seconds < 3600) {
      const minutes = Math.floor(seconds / 60)
      return `${minutes} minute${minutes !== 1 ? 's' : ''}`
    } else if (seconds < 86400) {
      const hours = Math.floor(seconds / 3600)
      return `${hours} hour${hours !== 1 ? 's' : ''}`
    } else {
      const days = Math.floor(seconds / 86400)
      return `${days} day${days !== 1 ? 's' : ''}`
    }
  }

  const getServiceStats = () => {
    // Get the latest status for each service
    const latestServices = {}
    services.forEach(service => {
      if (!latestServices[service.name] || new Date(service.timestamp) > new Date(latestServices[service.name].timestamp)) {
        latestServices[service.name] = service
      }
    })

    // Filter out redirect services and hosts for uptime calculation
    const monitorableServices = Object.values(latestServices).filter(service => 
      service.type !== 'redirect' && service.type !== 'host'
    )

    const upServices = monitorableServices.filter(service => service.status === 'up')
    const downServices = monitorableServices.filter(service => service.status === 'down')
    const totalServices = monitorableServices.length

    const uptimePercentage = totalServices > 0 ? Math.round((upServices.length / totalServices) * 100) : 0

    return {
      up: upServices.length,
      down: downServices.length,
      total: totalServices,
      uptimePercentage
    }
  }

  const ServiceCard = ({ service }) => {
    const [currentTime, setCurrentTime] = useState(new Date())
    
    // Update time every second for real-time duration display
    useEffect(() => {
      const interval = setInterval(() => {
        setCurrentTime(new Date())
      }, 1000)
      return () => clearInterval(interval)
    }, [])
    
    const getDurationText = () => {
      if (!service.status_since) return 'Unknown'
      
      const statusChangeTime = new Date(service.status_since)
      const diffMs = currentTime - statusChangeTime
      const diffSeconds = Math.floor(diffMs / 1000)
      const diffMinutes = Math.floor(diffSeconds / 60)
      const diffHours = Math.floor(diffMinutes / 60)
      const diffDays = Math.floor(diffHours / 24)
      
      if (diffDays > 0) {
        return `${diffDays}d ${diffHours % 24}h ${diffMinutes % 60}m`
      } else if (diffHours > 0) {
        return `${diffHours}h ${diffMinutes % 60}m`
      } else if (diffMinutes > 0) {
        return `${diffMinutes}m ${diffSeconds % 60}s`
      } else {
        return `${diffSeconds}s`
      }
    }
    
    return (
      <Card 
        sx={{ 
          borderLeft: 4, 
          borderColor: getStatusColor(service.status),
          height: '100%',
          display: 'flex',
          flexDirection: 'column'
        }}
      >
        <CardContent>
          <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
            <Box display="flex" alignItems="center">
              {getStatusIcon(service.status)}
              <Typography variant="h6" component="h3" ml={1}>
                {service.name}
              </Typography>
            </Box>
            {service.icon_url && (
              <Box 
                component="img"
                src={service.icon_url}
                alt={`${service.name} logo`}
                sx={{ 
                  width: 64, 
                  height: 64,
                  objectFit: 'contain',
                  opacity: 0.9
                }}
              />
            )}
          </Box>
          
          <Box>
            <Grid container spacing={1} mb={2}>
              {/* First row: Status and Uptime */}
              <Grid item xs={6}>
                <Box display="flex" alignItems="center">
                  <Typography variant="body2" color="text.secondary" mr={1}>
                    Status:
                  </Typography>
                  <Chip 
                    label={service.status === 'redirect' ? 'REDIRECT' : service.status.toUpperCase()} 
                    color={getStatusColor(service.status)}
                    size="small"
                  />
                </Box>
              </Grid>
              <Grid item xs={6}>
                {service.status_since && (
                  <Box display="flex" alignItems="center">
                    <Typography variant="body2" color="text.secondary" mr={1}>
                      {service.status === 'up' ? 'Uptime:' : 'Downtime:'}
                    </Typography>
                    <Typography variant="body2" fontFamily="monospace" color={getStatusColor(service.status) === 'success' ? 'success.main' : 'error.main'}>
                      {getDurationText()}
                    </Typography>
                  </Box>
                )}
              </Grid>
              
              {/* Second row: Response and Last check */}
              <Grid item xs={6}>
                {service.response_time !== null && (
                  <Box display="flex" alignItems="center">
                    <Typography variant="body2" color="text.secondary" mr={1}>
                      Response:
                    </Typography>
                    <Typography variant="body2" fontFamily="monospace">
                      {service.response_time}ms
                    </Typography>
                  </Box>
                )}
              </Grid>
              <Grid item xs={6}>
                {service.status_since && (
                  <Box display="flex" alignItems="center">
                    <AccessTimeIcon fontSize="small" color="action" sx={{ mr: 0.5 }} />
                    <Typography variant="caption" color="text.secondary">
                      {formatTimestamp(service.status_since)}
                    </Typography>
                  </Box>
                )}
              </Grid>
            </Grid>
            
            <Box display="flex" gap={1} flexWrap="wrap">
              {service.public_url && (
                <Button
                  variant="outlined"
                  size="small"
                  startIcon={<LaunchIcon />}
                  onClick={() => window.open(service.public_url, '_blank')}
                >
                  Visit
                </Button>
              )}
              {service.type !== 'redirect' && (
                <Button
                  variant="outlined"
                  size="small"
                  startIcon={<HistoryIcon />}
                  onClick={() => handleHistoryClick(service.name)}
                >
                  History
                </Button>
              )}
            </Box>
          </Box>
        </CardContent>
      </Card>
    )
  }

  const HostCard = ({ host }) => {
    const [currentTime, setCurrentTime] = useState(new Date())
    
    // Update time every second for real-time duration display
    useEffect(() => {
      const interval = setInterval(() => {
        setCurrentTime(new Date())
      }, 1000)
      return () => clearInterval(interval)
    }, [])
    
    const getDurationText = () => {
      if (!host.status_since) return 'Unknown'
      
      const statusChangeTime = new Date(host.status_since)
      const diffMs = currentTime - statusChangeTime
      const diffSeconds = Math.floor(diffMs / 1000)
      const diffMinutes = Math.floor(diffSeconds / 60)
      const diffHours = Math.floor(diffMinutes / 60)
      const diffDays = Math.floor(diffHours / 24)
      
      if (diffDays > 0) {
        return `${diffDays}d ${diffHours % 24}h ${diffMinutes % 60}m`
      } else if (diffHours > 0) {
        return `${diffHours}h ${diffMinutes % 60}m`
      } else if (diffMinutes > 0) {
        return `${diffMinutes}m ${diffSeconds % 60}s`
      } else {
        return `${diffSeconds}s`
      }
    }
    
    return (
      <Card 
        sx={{ 
          borderLeft: 4, 
          borderColor: getStatusColor(host.status),
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          mb: 2,
          backgroundColor: '#181825', // Darker background for host cards (Mantle color)
          '&:hover': {
            transform: 'none',
            boxShadow: 'none',
            backgroundColor: '#181825' // Keep the same darker background color on hover
          }
        }}
      >
        <CardContent>
          <Box display="flex" alignItems="center" mb={2}>
            <ComputerIcon color="primary" />
            <Typography variant="h5" component="h3" ml={1}>
              {host.name}
            </Typography>
            <Chip 
              label="HOST" 
              color="primary"
              size="small"
              sx={{ ml: 1 }}
            />
          </Box>
          
          <Box>
            <Box display="flex" alignItems="center" mb={1}>
              <Typography variant="body2" color="text.secondary" mr={1}>
                Status:
              </Typography>
              <Chip 
                label={host.status.toUpperCase()} 
                color={getStatusColor(host.status)}
                size="small"
              />
            </Box>
            
            {host.response_time !== null && (
              <Box display="flex" alignItems="center" mb={1}>
                <Typography variant="body2" color="text.secondary" mr={1}>
                  Response:
                </Typography>
                <Typography variant="body2" fontFamily="monospace">
                  {host.response_time}ms
                </Typography>
              </Box>
            )}
            
            {host.status_since && (
              <Box display="flex" alignItems="center" mb={1}>
                <Typography variant="body2" color="text.secondary" mr={1}>
                  {host.status === 'up' ? 'Uptime:' : 'Downtime:'}
                </Typography>
                <Typography variant="body2" fontFamily="monospace" color={getStatusColor(host.status) === 'success' ? 'success.main' : 'error.main'}>
                  {getDurationText()}
                </Typography>
              </Box>
            )}
            
            {host.status_since && (
              <Box display="flex" alignItems="center" mb={2}>
                <AccessTimeIcon fontSize="small" color="action" sx={{ mr: 0.5 }} />
                <Typography variant="caption" color="text.secondary">
                  Last check: {formatTimestamp(host.status_since)}
                </Typography>
              </Box>
            )}
            
            <Box display="flex" gap={1} flexWrap="wrap" mb={2}>
              <Button
                variant="outlined"
                size="small"
                startIcon={<HistoryIcon />}
                onClick={() => handleHistoryClick(host.name)}
              >
                History
              </Button>
            </Box>

            {/* Instances */}
            {host.instances.length > 0 && (
              <>
                <Divider sx={{ my: 2 }} />
                <Typography variant="h6" component="h4" gutterBottom>
                  Services ({host.instances.length})
                </Typography>
                
                {/* Group instances by category */}
                {(() => {
                  const instancesByCategory = {}
                  host.instances.forEach(instance => {
                    if (!instancesByCategory[instance.category]) {
                      instancesByCategory[instance.category] = []
                    }
                    instancesByCategory[instance.category].push(instance)
                  })

                  return categories.map(category => {
                    const categoryInstances = instancesByCategory[category] || []
                    if (categoryInstances.length === 0) return null

                    return (
                      <Box key={category} sx={{ mb: 3 }}>
                        <Typography 
                          variant="h6" 
                          component="h5" 
                          gutterBottom 
                          sx={{ 
                            color: 'text.secondary',
                            textTransform: 'uppercase',
                            fontSize: '1.1rem',
                            fontWeight: 600,
                            letterSpacing: '0.5px'
                          }}
                        >
                          {formatCategoryName(category)} ({categoryInstances.length})
                        </Typography>
                        <Grid container spacing={2}>
                          {categoryInstances.map((instance, index) => (
                            <Grid item xs={12} sm={6} md={4} key={index}>
                              <ServiceCard service={instance} />
                            </Grid>
                          ))}
                        </Grid>
                      </Box>
                    )
                  })
                })()}
              </>
            )}
          </Box>
        </CardContent>
      </Card>
    )
  }

  const DowntimeEvent = ({ event }) => (
    <Paper sx={{ p: 2, height: '100%' }}>
      <Typography variant="h6" color="error" gutterBottom>
        {event[0]}
      </Typography>
      <List dense>
        <ListItem sx={{ py: 0 }}>
          <ListItemIcon sx={{ minWidth: 36 }}>
            <ScheduleIcon fontSize="small" color="action" />
          </ListItemIcon>
          <ListItemText 
            primary="Start" 
            secondary={formatTimestamp(event[1])}
            primaryTypographyProps={{ variant: 'caption' }}
            secondaryTypographyProps={{ variant: 'body2' }}
          />
        </ListItem>
        {event[2] && (
          <ListItem sx={{ py: 0 }}>
            <ListItemIcon sx={{ minWidth: 36 }}>
              <CheckCircleIcon fontSize="small" color="success" />
            </ListItemIcon>
            <ListItemText 
              primary="End" 
              secondary={formatTimestamp(event[2])}
              primaryTypographyProps={{ variant: 'caption' }}
              secondaryTypographyProps={{ variant: 'body2' }}
            />
          </ListItem>
        )}
        {event[3] && (
          <ListItem sx={{ py: 0 }}>
            <ListItemIcon sx={{ minWidth: 36 }}>
              <TrendingUpIcon fontSize="small" color="action" />
            </ListItemIcon>
            <ListItemText 
              primary="Duration" 
              secondary={`${event[3]} minutes`}
              primaryTypographyProps={{ variant: 'caption' }}
              secondaryTypographyProps={{ variant: 'body2' }}
            />
          </ListItem>
        )}
        <ListItem sx={{ py: 0 }}>
          <ListItemText 
            primary="Status" 
            secondary={event[4] ? 'Resolved' : 'Ongoing'}
            primaryTypographyProps={{ variant: 'caption' }}
            secondaryTypographyProps={{ 
              variant: 'body2',
              color: event[4] ? 'success.main' : 'error.main'
            }}
          />
        </ListItem>
      </List>
    </Paper>
  )

  if (loading) {
    return (
      <ThemeProvider theme={darkTheme}>
        <CssBaseline />
        <Box 
          display="flex" 
          flexDirection="column" 
          alignItems="center" 
          justifyContent="center" 
          minHeight="100vh"
        >
          <CircularProgress size={60} />
          <Typography variant="h6" mt={2}>
            Loading services...
          </Typography>
        </Box>
      </ThemeProvider>
    )
  }

  if (error) {
    return (
      <ThemeProvider theme={darkTheme}>
        <CssBaseline />
        <Container maxWidth="sm" sx={{ mt: 8 }}>
          <Alert severity="error" sx={{ mb: 2 }}>
            <Typography variant="h6" gutterBottom>
              Error
            </Typography>
            <Typography>{error}</Typography>
          </Alert>
          <Button 
            variant="contained" 
            startIcon={<RefreshIcon />}
            onClick={fetchServices}
          >
            Retry
          </Button>
        </Container>
      </ThemeProvider>
    )
  }

  const groupedServices = getServicesByCategory()
  const { hosts, redirects, otherServices } = getServicesByHosts()

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Box sx={{ flexGrow: 1 }}>
        <AppBar position="static" elevation={0}>
          <Toolbar>
            <Box display="flex" alignItems="center" sx={{ flexGrow: 1 }}>
              <img src={logoLarge} alt="Logo" style={{ height: '40px', marginRight: '12px' }} />
              <Typography variant="h4" component="h1">
                Name Home Page
              </Typography>
            </Box>
            <Button 
              color="inherit" 
              startIcon={<RefreshIcon />}
              onClick={fetchServices}
            >
              Refresh
            </Button>
          </Toolbar>
        </AppBar>
        
        <Box sx={{ px: 4, py: 4 }}>
          <Typography variant="h5" component="h2" textAlign="center" gutterBottom>
            $WHOAMI
          </Typography>
          <Typography variant="h6" component="h2" textAlign="center" gutterBottom>
            Add a description here
          </Typography>
          {checkInterval && (
            <Typography variant="body1" textAlign="center" color="text.secondary" sx={{ mb: 2 }}>
              Services are checked every {formatInterval(checkInterval)}
            </Typography>
          )}
          
          {/* Service Summary */}
          {(() => {
            const stats = getServiceStats()
            if (stats.total > 0) {
              return (
                <Box sx={{ mb: 3 }}>
                  <Grid container spacing={2} justifyContent="center">
                    <Grid item>
                      <Paper sx={{ p: 2, textAlign: 'center', minWidth: 120 }}>
                        <Typography variant="h4" color="success.main" fontWeight="bold">
                          {stats.up}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Services Up
                        </Typography>
                      </Paper>
                    </Grid>
                    <Grid item>
                      <Paper sx={{ p: 2, textAlign: 'center', minWidth: 120 }}>
                        <Typography variant="h4" color="error.main" fontWeight="bold">
                          {stats.down}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Services Down
                        </Typography>
                      </Paper>
                    </Grid>
                    <Grid item>
                      <Paper sx={{ p: 2, textAlign: 'center', minWidth: 120 }}>
                        <Typography variant="h4" color="primary.main" fontWeight="bold">
                          {stats.uptimePercentage}%
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Uptime
                        </Typography>
                      </Paper>
                    </Grid>
                  </Grid>
                </Box>
              )
            }
            return null
          })()}
          
          <Divider sx={{ my: 3 }} />
          
          {/* Redirects Section */}
          {redirects.length > 0 && (
            <Box sx={{ mb: 4 }}>
              <Typography variant="h4" component="h2" gutterBottom textAlign="center">
                Quick Links
              </Typography>
              <Grid container spacing={3}>
                {redirects.map((service, index) => (
                  <Grid item xs={12} sm={6} md={4} key={index}>
                    <ServiceCard service={service} />
                  </Grid>
                ))}
              </Grid>
            </Box>
          )}

          {/* Hosts Section */}
          {Object.keys(hosts).length > 0 && (
            <Box sx={{ mb: 4 }}>
              <Typography variant="h4" component="h2" gutterBottom textAlign="center">
                Hosts & Services
              </Typography>
              <Grid container spacing={3}>
                {Object.values(hosts).map((host, index) => (
                  <Grid item xs={12} key={index}>
                    <HostCard host={host} />
                  </Grid>
                ))}
              </Grid>
            </Box>
          )}

          {/* Other Services Section */}
          {otherServices.length > 0 && (
            <Box sx={{ mb: 4 }}>
              <Typography variant="h4" component="h2" gutterBottom textAlign="center">
                Other Services
              </Typography>
              <Grid container spacing={3}>
                {otherServices.map((service, index) => (
                  <Grid item xs={12} sm={6} md={4} key={index}>
                    <ServiceCard service={service} />
                  </Grid>
                ))}
              </Grid>
            </Box>
          )}

          {downtimeEvents.length > 0 && (
            <>
              <Divider sx={{ my: 3 }} />
              <Typography variant="h4" component="h2" gutterBottom textAlign="center">
                Recent Downtime Events (Last 50 Checks)
              </Typography>
              <Grid container spacing={2}>
                {downtimeEvents.map((event, index) => (
                  <Grid item xs={12} sm={6} md={4} key={index}>
                    <DowntimeEvent event={event} />
                  </Grid>
                ))}
              </Grid>
            </>
          )}
        </Box>
      </Box>
      
      <ServiceHistoryChart
        open={historyChartOpen}
        onClose={() => setHistoryChartOpen(false)}
        serviceName={selectedService}
        historyData={historyData}
      />
    </ThemeProvider>
  )
}

export default App
