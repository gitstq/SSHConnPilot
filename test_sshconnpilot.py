#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSHConnPilot Unit Tests
"""

import unittest
import json
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import the module
import sshconnpilot as scp


class TestConfigManager(unittest.TestCase):
    """Test ConfigManager class"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.config_dir = Path(self.test_dir) / ".sshconnpilot"
        
        # Patch the config directory
        self.original_init = scp.ConfigManager.__init__
        
        def patched_init(self):
            self.config_dir = Path(self.test_dir) / ".sshconnpilot"
            self.config_file = self.config_dir / "config.json"
            self.hosts_file = self.config_dir / "hosts.json"
            self.history_file = self.config_dir / "history.json"
            self._ensure_config_dir()
        
        scp.ConfigManager.__init__ = patched_init
        self.config = scp.ConfigManager()
    
    def tearDown(self):
        """Clean up test environment"""
        scp.ConfigManager.__init__ = self.original_init
        shutil.rmtree(self.test_dir)
    
    def test_config_dir_creation(self):
        """Test configuration directory is created"""
        self.assertTrue(self.config.config_dir.exists())
    
    def test_default_config(self):
        """Test default configuration loading"""
        config = self.config.load_config()
        self.assertIn("version", config)
        self.assertIn("default_port", config)
        self.assertEqual(config["default_port"], 22)
    
    def test_save_and_load_hosts(self):
        """Test saving and loading hosts"""
        test_hosts = {
            "test-server": {
                "hostname": "192.168.1.100",
                "user": "admin",
                "port": 22,
                "tags": ["test"]
            }
        }
        self.config.save_hosts(test_hosts)
        loaded = self.config.load_hosts()
        self.assertEqual(loaded["test-server"]["hostname"], "192.168.1.100")
    
    def test_save_and_load_history(self):
        """Test saving and loading history"""
        test_history = [
            {"name": "server1", "hostname": "192.168.1.1", "timestamp": "2025-01-01T00:00:00"}
        ]
        self.config.save_history(test_history)
        loaded = self.config.load_history()
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0]["name"], "server1")


class TestCredentialManager(unittest.TestCase):
    """Test CredentialManager class"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.config_dir = Path(self.test_dir)
        self.cred_manager = scp.CredentialManager(self.config_dir)
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir)
    
    def test_save_and_get_credential(self):
        """Test saving and retrieving credentials"""
        self.cred_manager.save_credential("test-host", "my-password")
        retrieved = self.cred_manager.get_credential("test-host")
        self.assertEqual(retrieved, "my-password")
    
    def test_get_nonexistent_credential(self):
        """Test retrieving non-existent credential"""
        result = self.cred_manager.get_credential("nonexistent")
        self.assertIsNone(result)
    
    def test_delete_credential(self):
        """Test deleting credentials"""
        self.cred_manager.save_credential("test-host", "my-password")
        self.cred_manager.delete_credential("test-host")
        result = self.cred_manager.get_credential("test-host")
        self.assertIsNone(result)


class TestSSHManager(unittest.TestCase):
    """Test SSHManager class"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        
        # Patch ConfigManager
        self.original_config_init = scp.ConfigManager.__init__
        
        def patched_config_init(self):
            self.config_dir = Path(self.test_dir) / ".sshconnpilot"
            self.config_file = self.config_dir / "config.json"
            self.hosts_file = self.config_dir / "hosts.json"
            self.history_file = self.config_dir / "history.json"
            self._ensure_config_dir()
        
        scp.ConfigManager.__init__ = patched_config_init
        self.manager = scp.SSHManager()
    
    def tearDown(self):
        """Clean up test environment"""
        scp.ConfigManager.__init__ = self.original_config_init
        shutil.rmtree(self.test_dir)
    
    def test_add_host(self):
        """Test adding a host"""
        result = self.manager.add_host(
            "test-server",
            "192.168.1.100",
            user="admin",
            port=2222,
            description="Test server",
            tags=["test", "local"]
        )
        self.assertTrue(result)
        self.assertIn("test-server", self.manager.hosts)
        self.assertEqual(self.manager.hosts["test-server"]["port"], 2222)
    
    def test_add_duplicate_host(self):
        """Test adding duplicate host fails"""
        self.manager.add_host("test-server", "192.168.1.100")
        result = self.manager.add_host("test-server", "192.168.1.101")
        self.assertFalse(result)
    
    def test_update_host(self):
        """Test updating a host"""
        self.manager.add_host("test-server", "192.168.1.100", user="admin")
        result = self.manager.update_host("test-server", user="root")
        self.assertTrue(result)
        self.assertEqual(self.manager.hosts["test-server"]["user"], "root")
    
    def test_update_nonexistent_host(self):
        """Test updating non-existent host fails"""
        result = self.manager.update_host("nonexistent", user="root")
        self.assertFalse(result)
    
    def test_remove_host(self):
        """Test removing a host"""
        self.manager.add_host("test-server", "192.168.1.100")
        result = self.manager.remove_host("test-server")
        self.assertTrue(result)
        self.assertNotIn("test-server", self.manager.hosts)
    
    def test_remove_nonexistent_host(self):
        """Test removing non-existent host fails"""
        result = self.manager.remove_host("nonexistent")
        self.assertFalse(result)
    
    def test_ai_suggest(self):
        """Test AI suggestions"""
        suggestions = self.manager._generate_suggestions("AWS EC2 Ubuntu production server")
        self.assertIn("tags", suggestions)
        self.assertIn("aws", suggestions["tags"])
        self.assertIn("ubuntu", suggestions["tags"])
        self.assertEqual(suggestions["user"], "ubuntu")
    
    def test_ai_suggest_centos(self):
        """Test AI suggestions for CentOS"""
        suggestions = self.manager._generate_suggestions("CentOS development server")
        self.assertIn("centos", suggestions["tags"])
        self.assertEqual(suggestions["user"], "root")
    
    def test_export_import_json(self):
        """Test JSON export and import"""
        self.manager.add_host("server1", "192.168.1.1")
        self.manager.add_host("server2", "192.168.1.2")
        
        export_file = Path(self.test_dir) / "export.json"
        self.manager.export_config(str(export_file), "json")
        
        # Clear hosts
        self.manager.hosts = {}
        self.manager.config.save_hosts({})
        
        # Import
        self.manager.import_config(str(export_file), "json")
        self.assertIn("server1", self.manager.hosts)
        self.assertIn("server2", self.manager.hosts)


class TestIntegration(unittest.TestCase):
    """Integration tests"""
    
    def test_full_workflow(self):
        """Test complete workflow"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Patch config directory
            original_init = scp.ConfigManager.__init__
            
            def patched_init(self):
                self.config_dir = Path(tmpdir) / ".sshconnpilot"
                self.config_file = self.config_dir / "config.json"
                self.hosts_file = self.config_dir / "hosts.json"
                self.history_file = self.config_dir / "history.json"
                self._ensure_config_dir()
            
            scp.ConfigManager.__init__ = patched_init
            
            try:
                manager = scp.SSHManager()
                
                # Add hosts
                manager.add_host("web-server", "192.168.1.10", user="ubuntu", tags=["web", "prod"])
                manager.add_host("db-server", "192.168.1.11", user="root", tags=["db", "prod"])
                
                # Update host
                manager.update_host("web-server", port=2222)
                
                # Verify
                self.assertEqual(manager.hosts["web-server"]["port"], 2222)
                self.assertEqual(len(manager.hosts), 2)
                
                # Remove host
                manager.remove_host("db-server")
                self.assertEqual(len(manager.hosts), 1)
                
            finally:
                scp.ConfigManager.__init__ = original_init


if __name__ == "__main__":
    unittest.main()
