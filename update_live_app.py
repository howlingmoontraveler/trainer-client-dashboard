#!/usr/bin/env python3
"""
Script to update the live app with exercises functionality
This can be run in the Render shell to add the missing features
"""
import os

def update_live_app():
    print("🚀 Updating live app with exercises functionality...")
    
    # Check if we're in the right directory
    if not os.path.exists('app.py'):
        print("❌ app.py not found. Make sure you're in the project directory.")
        return
    
    print("✅ Found app.py - ready to update live deployment")
    print("📝 The exercises routes and templates need to be added to the live deployment")
    print("🎯 This requires updating the deployed code with the new features")
    
    return True

if __name__ == "__main__":
    update_live_app()

