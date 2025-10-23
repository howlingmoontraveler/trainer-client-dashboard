#!/bin/bash
cd /home/user/trainer-client-dashboard
echo "========================================="
echo "Starting Trainer-Client Dashboard"
echo "========================================="
echo ""
echo "Access the application at:"
echo "  http://localhost:5000"
echo "  or"
echo "  http://127.0.0.1:5000"
echo ""
echo "Demo Accounts:"
echo "  Trainer: trainer1 / password123"
echo "  Client:  client1 / password123"
echo ""
echo "Press CTRL+C to stop the server"
echo "========================================="
echo ""
python3 app.py
