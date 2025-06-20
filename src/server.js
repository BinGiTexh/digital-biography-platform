import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import compression from 'compression';
import dotenv from 'dotenv';
import { createServer } from 'http';
import { Server } from 'socket.io';

// Load environment variables
dotenv.config();

const app = express();
const server = createServer(app);
const io = new Server(server, {
  cors: {
    origin: process.env.CORS_ORIGIN || "*",
    methods: ["GET", "POST"]
  }
});

const PORT = process.env.PORT || 3001;

// Middleware
app.use(helmet());
app.use(compression());
app.use(cors());
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    service: 'BingiTech Digital Biography Platform',
    version: '1.0.0',
    environment: process.env.NODE_ENV || 'development'
  });
});

// API routes
app.get('/api/status', (req, res) => {
  res.json({
    message: 'BingiTech Digital Biography Platform API',
    endpoints: {
      health: '/health',
      status: '/api/status',
      content: '/api/content',
      agents: '/api/agents'
    }
  });
});

// Content generation endpoint
app.post('/api/content/generate', async (req, res) => {
  try {
    const { type, topic, platform } = req.body;
    
    // Placeholder for content generation logic
    res.json({
      success: true,
      message: 'Content generation request received',
      data: {
        type,
        topic,
        platform,
        timestamp: new Date().toISOString()
      }
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Content generation failed',
      error: error.message
    });
  }
});

// Agent system status
app.get('/api/agents/status', (req, res) => {
  res.json({
    agents: {
      content_strategist: 'active',
      twitter_agent: 'active',
      linkedin_agent: 'active',
      content_creator: 'active'
    },
    last_activity: new Date().toISOString()
  });
});

// WebSocket for real-time updates
io.on('connection', (socket) => {
  console.log('Client connected:', socket.id);
  
  socket.emit('welcome', {
    message: 'Connected to BingiTech Digital Biography Platform',
    clientId: socket.id
  });
  
  socket.on('disconnect', () => {
    console.log('Client disconnected:', socket.id);
  });
});

// Error handling middleware
app.use((error, req, res, next) => {
  console.error('Error:', error);
  res.status(500).json({
    success: false,
    message: 'Internal server error',
    error: process.env.NODE_ENV === 'development' ? error.message : 'Something went wrong'
  });
});

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({
    success: false,
    message: 'Endpoint not found',
    path: req.originalUrl
  });
});

// Start server
server.listen(PORT, () => {
  console.log(`🚀 BingiTech Digital Biography Platform API running on port ${PORT}`);
  console.log(`🌐 Environment: ${process.env.NODE_ENV || 'development'}`);
  console.log(`📊 Health check: http://localhost:${PORT}/health`);
  console.log(`📋 API status: http://localhost:${PORT}/api/status`);
});

export default app;

