#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSHConnPilot - Lightweight AI-Powered SSH Connection Intelligence Manager CLI
轻量级AI驱动SSH连接智能管理CLI工具

A zero-dependency Python CLI tool for intelligent SSH connection management
with AI-assisted configuration, secure credential storage, and connection analytics.
"""

import argparse
import json
import os
import re
import sys
import subprocess
import getpass
import hashlib
import base64
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

__version__ = "1.0.0"
__author__ = "SSHConnPilot Team"
__license__ = "MIT"


class Colors:
    """Terminal color codes for beautiful output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class ConfigManager:
    """Manages configuration and data storage"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".sshconnpilot"
        self.config_file = self.config_dir / "config.json"
        self.hosts_file = self.config_dir / "hosts.json"
        self.history_file = self.config_dir / "history.json"
        self._ensure_config_dir()
    
    def _ensure_config_dir(self):
        """Ensure configuration directory exists"""
        self.config_dir.mkdir(exist_ok=True)
        # Set restrictive permissions (700)
        os.chmod(self.config_dir, 0o700)
    
    def load_config(self) -> Dict:
        """Load main configuration"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return self._default_config()
    
    def save_config(self, config: Dict):
        """Save main configuration"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        os.chmod(self.config_file, 0o600)
    
    def load_hosts(self) -> Dict:
        """Load hosts configuration"""
        if self.hosts_file.exists():
            with open(self.hosts_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def save_hosts(self, hosts: Dict):
        """Save hosts configuration"""
        with open(self.hosts_file, 'w', encoding='utf-8') as f:
            json.dump(hosts, f, indent=2, ensure_ascii=False)
        os.chmod(self.hosts_file, 0o600)
    
    def load_history(self) -> List:
        """Load connection history"""
        if self.history_file.exists():
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def save_history(self, history: List):
        """Save connection history"""
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
        os.chmod(self.history_file, 0o600)
    
    def _default_config(self) -> Dict:
        """Return default configuration"""
        return {
            "version": __version__,
            "default_user": getpass.getuser(),
            "default_port": 22,
            "ai_suggestions_enabled": True,
            "connection_timeout": 30,
            "keep_history": True,
            "max_history_entries": 1000,
            "theme": "default"
        }


class CredentialManager:
    """Manages secure credential storage (basic encryption)"""
    
    def __init__(self, config_dir: Path):
        self.cred_file = config_dir / ".creds"
        self._key = self._derive_key()
    
    def _derive_key(self) -> bytes:
        """Derive encryption key from system-specific data"""
        # Use a combination of system info to create a unique key
        system_data = f"{os.uname().nodename}{os.getuid()}{Path.home()}"
        return hashlib.sha256(system_data.encode()).digest()[:32]
    
    def _xor_encrypt(self, data: str) -> str:
        """Simple XOR encryption (sufficient for local protection)"""
        encrypted = []
        for i, char in enumerate(data):
            encrypted.append(chr(ord(char) ^ self._key[i % len(self._key)]))
        return base64.b64encode(''.join(encrypted).encode()).decode()
    
    def _xor_decrypt(self, data: str) -> str:
        """Decrypt XOR encrypted data"""
        try:
            decoded = base64.b64decode(data).decode()
            decrypted = []
            for i, char in enumerate(decoded):
                decrypted.append(chr(ord(char) ^ self._key[i % len(self._key)]))
            return ''.join(decrypted)
        except Exception:
            return ""
    
    def save_credential(self, host_id: str, password: str):
        """Save encrypted credential"""
        creds = {}
        if self.cred_file.exists():
            with open(self.cred_file, 'r') as f:
                creds = json.load(f)
        
        creds[host_id] = self._xor_encrypt(password)
        
        with open(self.cred_file, 'w') as f:
            json.dump(creds, f)
        os.chmod(self.cred_file, 0o600)
    
    def get_credential(self, host_id: str) -> Optional[str]:
        """Retrieve decrypted credential"""
        if not self.cred_file.exists():
            return None
        
        with open(self.cred_file, 'r') as f:
            creds = json.load(f)
        
        if host_id in creds:
            return self._xor_decrypt(creds[host_id])
        return None
    
    def delete_credential(self, host_id: str):
        """Delete stored credential"""
        if self.cred_file.exists():
            with open(self.cred_file, 'r') as f:
                creds = json.load(f)
            
            if host_id in creds:
                del creds[host_id]
                with open(self.cred_file, 'w') as f:
                    json.dump(creds, f)


class SSHManager:
    """Main SSH connection manager"""
    
    def __init__(self):
        self.config = ConfigManager()
        self.settings = self.config.load_config()
        self.hosts = self.config.load_hosts()
        self.history = self.config.load_history()
        self.credentials = CredentialManager(self.config.config_dir)
    
    def print_banner(self):
        """Print application banner"""
        banner = f"""
{Colors.CYAN}╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   🔐 SSHConnPilot - AI-Powered SSH Connection Manager      ║
║                                                              ║
║   Version: {__version__}                                         ║
║   Light-weight • Zero-dependency • AI-Assisted              ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝{Colors.ENDC}
"""
        print(banner)
    
    def print_success(self, message: str):
        """Print success message"""
        print(f"{Colors.GREEN}✓ {message}{Colors.ENDC}")
    
    def print_error(self, message: str):
        """Print error message"""
        print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")
    
    def print_warning(self, message: str):
        """Print warning message"""
        print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")
    
    def print_info(self, message: str):
        """Print info message"""
        print(f"{Colors.BLUE}ℹ {message}{Colors.ENDC}")
    
    def add_host(self, name: str, hostname: str, user: str = None, 
                 port: int = 22, identity_file: str = None, 
                 description: str = None, tags: List[str] = None):
        """Add a new SSH host"""
        if name in self.hosts:
            self.print_error(f"Host '{name}' already exists. Use 'update' to modify.")
            return False
        
        self.hosts[name] = {
            "hostname": hostname,
            "user": user or self.settings.get("default_user", getpass.getuser()),
            "port": port,
            "identity_file": identity_file,
            "description": description or "",
            "tags": tags or [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "connect_count": 0,
            "last_connected": None
        }
        
        self.config.save_hosts(self.hosts)
        self.print_success(f"Host '{name}' added successfully!")
        return True
    
    def update_host(self, name: str, **kwargs):
        """Update existing host configuration"""
        if name not in self.hosts:
            self.print_error(f"Host '{name}' not found.")
            return False
        
        for key, value in kwargs.items():
            if value is not None and key in self.hosts[name]:
                self.hosts[name][key] = value
        
        self.hosts[name]["updated_at"] = datetime.now().isoformat()
        self.config.save_hosts(self.hosts)
        self.print_success(f"Host '{name}' updated successfully!")
        return True
    
    def remove_host(self, name: str):
        """Remove a host configuration"""
        if name not in self.hosts:
            self.print_error(f"Host '{name}' not found.")
            return False
        
        del self.hosts[name]
        self.credentials.delete_credential(name)
        self.config.save_hosts(self.hosts)
        self.print_success(f"Host '{name}' removed successfully!")
        return True
    
    def list_hosts(self, tag: str = None, search: str = None):
        """List all configured hosts"""
        if not self.hosts:
            self.print_warning("No hosts configured. Use 'add' to add a new host.")
            return
        
        filtered_hosts = self.hosts
        
        if tag:
            filtered_hosts = {k: v for k, v in filtered_hosts.items() 
                           if tag in v.get("tags", [])}
        
        if search:
            filtered_hosts = {k: v for k, v in filtered_hosts.items() 
                           if search.lower() in k.lower() or 
                           search.lower() in v.get("description", "").lower()}
        
        if not filtered_hosts:
            self.print_warning("No hosts match the filter criteria.")
            return
        
        print(f"\n{Colors.BOLD}Configured SSH Hosts ({len(filtered_hosts)} total):{Colors.ENDC}\n")
        print(f"{'Name':<20} {'Host':<25} {'User':<15} {'Port':<6} {'Tags':<20}")
        print("-" * 90)
        
        for name, host in sorted(filtered_hosts.items()):
            tags_str = ", ".join(host.get("tags", []))[:18]
            print(f"{Colors.CYAN}{name:<20}{Colors.ENDC} "
                  f"{host['hostname']:<25} "
                  f"{host['user']:<15} "
                  f"{host['port']:<6} "
                  f"{Colors.GREEN}{tags_str:<20}{Colors.ENDC}")
            
            if host.get("description"):
                print(f"  {Colors.BLUE}↳ {host['description'][:60]}{Colors.ENDC}")
        
        print()
    
    def show_host(self, name: str):
        """Show detailed host information"""
        if name not in self.hosts:
            self.print_error(f"Host '{name}' not found.")
            return
        
        host = self.hosts[name]
        print(f"\n{Colors.BOLD}Host Details: {name}{Colors.ENDC}\n")
        print(f"  {Colors.CYAN}Hostname:{Colors.ENDC}     {host['hostname']}")
        print(f"  {Colors.CYAN}User:{Colors.ENDC}         {host['user']}")
        print(f"  {Colors.CYAN}Port:{Colors.ENDC}         {host['port']}")
        print(f"  {Colors.CYAN}Description:{Colors.ENDC}  {host.get('description', 'N/A')}")
        print(f"  {Colors.CYAN}Tags:{Colors.ENDC}         {', '.join(host.get('tags', [])) or 'N/A'}")
        print(f"  {Colors.CYAN}Identity File:{Colors.ENDC} {host.get('identity_file', 'N/A')}")
        print(f"  {Colors.CYAN}Created:{Colors.ENDC}      {host.get('created_at', 'N/A')}")
        print(f"  {Colors.CYAN}Updated:{Colors.ENDC}      {host.get('updated_at', 'N/A')}")
        print(f"  {Colors.CYAN}Connections:{Colors.ENDC}  {host.get('connect_count', 0)}")
        print(f"  {Colors.CYAN}Last Connected:{Colors.ENDC} {host.get('last_connected', 'Never')}")
        print()
    
    def connect(self, name: str, password: str = None):
        """Connect to a host via SSH"""
        if name not in self.hosts:
            self.print_error(f"Host '{name}' not found.")
            return False
        
        host = self.hosts[name]
        
        # Build SSH command
        cmd = ["ssh"]
        
        if host.get("identity_file"):
            cmd.extend(["-i", host["identity_file"]])
        
        cmd.extend(["-p", str(host["port"])])
        cmd.extend(["-o", f"ConnectTimeout={self.settings.get('connection_timeout', 30)}"])
        cmd.extend(["-o", "StrictHostKeyChecking=accept-new"])
        
        target = f"{host['user']}@{host['hostname']}"
        cmd.append(target)
        
        # Update statistics
        self.hosts[name]["connect_count"] = self.hosts[name].get("connect_count", 0) + 1
        self.hosts[name]["last_connected"] = datetime.now().isoformat()
        self.config.save_hosts(self.hosts)
        
        # Add to history
        self._add_history(name, host["hostname"])
        
        self.print_info(f"Connecting to {name} ({target})...")
        print(f"{Colors.CYAN}Command: {' '.join(cmd)}{Colors.ENDC}\n")
        
        try:
            # Execute SSH command
            subprocess.call(cmd)
            return True
        except KeyboardInterrupt:
            print(f"\n{Colors.WARNING}Connection interrupted.{Colors.ENDC}")
            return False
    
    def _add_history(self, name: str, hostname: str):
        """Add connection to history"""
        if not self.settings.get("keep_history", True):
            return
        
        entry = {
            "name": name,
            "hostname": hostname,
            "timestamp": datetime.now().isoformat()
        }
        
        self.history.insert(0, entry)
        
        # Keep only max entries
        max_entries = self.settings.get("max_history_entries", 1000)
        self.history = self.history[:max_entries]
        
        self.config.save_history(self.history)
    
    def show_history(self, limit: int = 20):
        """Show connection history"""
        if not self.history:
            self.print_warning("No connection history.")
            return
        
        print(f"\n{Colors.BOLD}Recent Connections (last {min(limit, len(self.history))}):{Colors.ENDC}\n")
        print(f"{'Time':<25} {'Name':<20} {'Hostname':<30}")
        print("-" * 75)
        
        for entry in self.history[:limit]:
            time_str = entry["timestamp"][:19].replace("T", " ")
            print(f"{time_str:<25} {Colors.CYAN}{entry['name']:<20}{Colors.ENDC} {entry['hostname']:<30}")
        
        print()
    
    def quick_connect(self, hostname: str, user: str = None, port: int = 22):
        """Quick connect without saving"""
        user = user or self.settings.get("default_user", getpass.getuser())
        
        cmd = ["ssh", "-p", str(port), f"{user}@{hostname}"]
        
        self.print_info(f"Quick connecting to {user}@{hostname}...")
        print(f"{Colors.CYAN}Command: {' '.join(cmd)}{Colors.ENDC}\n")
        
        try:
            subprocess.call(cmd)
        except KeyboardInterrupt:
            print(f"\n{Colors.WARNING}Connection interrupted.{Colors.ENDC}")
    
    def ai_suggest(self, description: str):
        """AI-assisted host configuration suggestion"""
        print(f"\n{Colors.BOLD}🤖 AI Configuration Assistant{Colors.ENDC}\n")
        
        # Simple rule-based suggestions (can be enhanced with actual AI)
        suggestions = self._generate_suggestions(description)
        
        print(f"Based on your description: '{description}'\n")
        print(f"{Colors.CYAN}Suggested Configuration:{Colors.ENDC}\n")
        
        for key, value in suggestions.items():
            print(f"  {Colors.GREEN}• {key}:{Colors.ENDC} {value}")
        
        print(f"\n{Colors.WARNING}Note: These are template suggestions. Please verify before use.{Colors.ENDC}\n")
        
        return suggestions
    
    def _generate_suggestions(self, description: str) -> Dict:
        """Generate configuration suggestions based on description"""
        desc_lower = description.lower()
        suggestions = {
            "name": "my-server",
            "hostname": "example.com",
            "user": "root",
            "port": 22,
            "tags": []
        }
        
        # Extract potential hostname
        host_pattern = r'(?:[\w-]+\.)+[\w-]+'
        hosts = re.findall(host_pattern, description)
        if hosts:
            suggestions["hostname"] = hosts[0]
            suggestions["name"] = hosts[0].split('.')[0]
        
        # Detect common patterns
        if any(word in desc_lower for word in ["aws", "ec2", "amazon"]):
            suggestions["user"] = "ec2-user"
            suggestions["tags"].append("aws")
        elif any(word in desc_lower for word in ["ubuntu", "debian"]):
            suggestions["user"] = "ubuntu"
            suggestions["tags"].append("ubuntu")
        elif any(word in desc_lower for word in ["centos", "rhel", "redhat", "fedora"]):
            suggestions["user"] = "root"
            suggestions["tags"].append("centos")
        
        if any(word in desc_lower for word in ["production", "prod"]):
            suggestions["tags"].append("production")
        elif any(word in desc_lower for word in ["development", "dev", "test"]):
            suggestions["tags"].append("development")
        
        if "docker" in desc_lower:
            suggestions["tags"].append("docker")
        
        if "kubernetes" in desc_lower or "k8s" in desc_lower:
            suggestions["tags"].append("kubernetes")
        
        return suggestions
    
    def test_connection(self, name: str) -> bool:
        """Test SSH connection without fully connecting"""
        if name not in self.hosts:
            self.print_error(f"Host '{name}' not found.")
            return False
        
        host = self.hosts[name]
        target = f"{host['user']}@{host['hostname']}"
        
        cmd = [
            "ssh",
            "-p", str(host["port"]),
            "-o", "ConnectTimeout=5",
            "-o", "BatchMode=yes",
            "-o", "StrictHostKeyChecking=accept-new",
            target,
            "echo 'Connection successful!'"
        ]
        
        self.print_info(f"Testing connection to {name}...")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.print_success(f"Connection to {name} successful!")
                return True
            else:
                self.print_error(f"Connection failed: {result.stderr.strip()}")
                return False
        except subprocess.TimeoutExpired:
            self.print_error("Connection timed out.")
            return False
        except Exception as e:
            self.print_error(f"Error: {str(e)}")
            return False
    
    def export_config(self, output_file: str, format_type: str = "json"):
        """Export configuration to file"""
        export_data = {
            "version": __version__,
            "export_date": datetime.now().isoformat(),
            "hosts": self.hosts,
            "settings": self.settings
        }
        
        if format_type == "json":
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
        elif format_type == "ssh_config":
            # Export to OpenSSH config format
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"# SSHConnPilot Export - {datetime.now().isoformat()}\n\n")
                for name, host in self.hosts.items():
                    f.write(f"Host {name}\n")
                    f.write(f"    HostName {host['hostname']}\n")
                    f.write(f"    User {host['user']}\n")
                    f.write(f"    Port {host['port']}\n")
                    if host.get("identity_file"):
                        f.write(f"    IdentityFile {host['identity_file']}\n")
                    f.write("\n")
        
        self.print_success(f"Configuration exported to {output_file}")
    
    def import_config(self, input_file: str, format_type: str = "json"):
        """Import configuration from file"""
        try:
            if format_type == "json":
                with open(input_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if "hosts" in data:
                    imported_count = 0
                    for name, host in data["hosts"].items():
                        if name not in self.hosts:
                            self.hosts[name] = host
                            imported_count += 1
                    
                    self.config.save_hosts(self.hosts)
                    self.print_success(f"Imported {imported_count} hosts from {input_file}")
            
            elif format_type == "ssh_config":
                # Parse OpenSSH config format
                imported_count = self._parse_ssh_config(input_file)
                self.print_success(f"Imported {imported_count} hosts from {input_file}")
        
        except Exception as e:
            self.print_error(f"Import failed: {str(e)}")
    
    def _parse_ssh_config(self, filepath: str) -> int:
        """Parse OpenSSH config file"""
        count = 0
        current_host = None
        
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                parts = line.split(None, 1)
                if len(parts) < 2:
                    continue
                
                key, value = parts[0], parts[1]
                
                if key.lower() == "host" and not value.startswith("*"):
                    current_host = value
                    self.hosts[current_host] = {
                        "hostname": value,
                        "user": self.settings.get("default_user", getpass.getuser()),
                        "port": 22,
                        "tags": ["imported"],
                        "created_at": datetime.now().isoformat(),
                        "updated_at": datetime.now().isoformat(),
                        "connect_count": 0
                    }
                    count += 1
                elif current_host:
                    if key.lower() == "hostname":
                        self.hosts[current_host]["hostname"] = value
                    elif key.lower() == "user":
                        self.hosts[current_host]["user"] = value
                    elif key.lower() == "port":
                        self.hosts[current_host]["port"] = int(value)
                    elif key.lower() == "identityfile":
                        self.hosts[current_host]["identity_file"] = value
        
        self.config.save_hosts(self.hosts)
        return count
    
    def show_stats(self):
        """Show connection statistics"""
        print(f"\n{Colors.BOLD}📊 Connection Statistics{Colors.ENDC}\n")
        
        total_hosts = len(self.hosts)
        total_connections = sum(h.get("connect_count", 0) for h in self.hosts.values())
        
        print(f"  {Colors.CYAN}Total Hosts:{Colors.ENDC}        {total_hosts}")
        print(f"  {Colors.CYAN}Total Connections:{Colors.ENDC}  {total_connections}")
        print(f"  {Colors.CYAN}History Entries:{Colors.ENDC}    {len(self.history)}")
        
        if self.hosts:
            print(f"\n{Colors.BOLD}Top Connected Hosts:{Colors.ENDC}\n")
            sorted_hosts = sorted(self.hosts.items(), 
                                 key=lambda x: x[1].get("connect_count", 0), 
                                 reverse=True)[:5]
            
            for name, host in sorted_hosts:
                count = host.get("connect_count", 0)
                bar = "█" * min(count, 20)
                print(f"  {Colors.CYAN}{name:<20}{Colors.ENDC} {bar} {count}")
        
        print()
    
    def interactive_shell(self):
        """Run interactive shell mode"""
        self.print_banner()
        self.print_info("Entering interactive mode. Type 'help' for commands, 'exit' to quit.\n")
        
        while True:
            try:
                command = input(f"{Colors.GREEN}sshcp>{Colors.ENDC} ").strip()
                
                if not command:
                    continue
                
                parts = command.split()
                cmd = parts[0].lower()
                args = parts[1:]
                
                if cmd in ["exit", "quit"]:
                    print(f"{Colors.CYAN}Goodbye! 👋{Colors.ENDC}")
                    break
                elif cmd == "help":
                    self._print_interactive_help()
                elif cmd == "list":
                    self.list_hosts()
                elif cmd == "add":
                    self._interactive_add()
                elif cmd == "connect" and args:
                    self.connect(args[0])
                elif cmd == "quick":
                    self._interactive_quick()
                elif cmd == "stats":
                    self.show_stats()
                elif cmd == "history":
                    self.show_history()
                else:
                    print(f"{Colors.WARNING}Unknown command. Type 'help' for available commands.{Colors.ENDC}")
            
            except KeyboardInterrupt:
                print(f"\n{Colors.CYAN}Use 'exit' to quit.{Colors.ENDC}")
            except EOFError:
                break
    
    def _print_interactive_help(self):
        """Print help for interactive mode"""
        help_text = f"""
{Colors.BOLD}Available Commands:{Colors.ENDC}

  {Colors.CYAN}list{Colors.ENDC}              List all configured hosts
  {Colors.CYAN}add{Colors.ENDC}               Add a new host interactively
  {Colors.CYAN}connect <name>{Colors.ENDC}    Connect to a host
  {Colors.CYAN}quick{Colors.ENDC}             Quick connect without saving
  {Colors.CYAN}stats{Colors.ENDC}             Show connection statistics
  {Colors.CYAN}history{Colors.ENDC}           Show connection history
  {Colors.CYAN}help{Colors.ENDC}              Show this help message
  {Colors.CYAN}exit/quit{Colors.ENDC}         Exit interactive mode
"""
        print(help_text)
    
    def _interactive_add(self):
        """Interactive add host"""
        print(f"\n{Colors.BOLD}Add New Host{Colors.ENDC}\n")
        
        name = input("Host name (alias): ").strip()
        if not name:
            self.print_error("Host name is required.")
            return
        
        hostname = input("Hostname/IP: ").strip()
        if not hostname:
            self.print_error("Hostname is required.")
            return
        
        user = input(f"User [{self.settings.get('default_user', getpass.getuser())}]: ").strip()
        port_str = input("Port [22]: ").strip()
        description = input("Description: ").strip()
        tags_str = input("Tags (comma-separated): ").strip()
        
        port = int(port_str) if port_str else 22
        user = user or self.settings.get("default_user", getpass.getuser())
        tags = [t.strip() for t in tags_str.split(",") if t.strip()]
        
        self.add_host(name, hostname, user, port, description=description, tags=tags)
    
    def _interactive_quick(self):
        """Interactive quick connect"""
        print(f"\n{Colors.BOLD}Quick Connect{Colors.ENDC}\n")
        
        hostname = input("Hostname/IP: ").strip()
        if not hostname:
            self.print_error("Hostname is required.")
            return
        
        user = input(f"User [{self.settings.get('default_user', getpass.getuser())}]: ").strip()
        port_str = input("Port [22]: ").strip()
        
        port = int(port_str) if port_str else 22
        user = user or self.settings.get("default_user", getpass.getuser())
        
        self.quick_connect(hostname, user, port)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="SSHConnPilot - AI-Powered SSH Connection Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Launch interactive mode
  %(prog)s list                     # List all hosts
  %(prog)s add -n web1 --host 192.168.1.10 -u admin  # Add new host
  %(prog)s connect web1             # Connect to host
  %(prog)s quick --host server.com -u root  # Quick connect
  %(prog)s suggest "AWS EC2 Ubuntu production"  # Get AI suggestions
        """
    )
    
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # List command
    subparsers.add_parser("list", help="List all configured hosts")
    
    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new host")
    add_parser.add_argument("-n", "--name", required=True, help="Host alias name")
    add_parser.add_argument("--host", required=True, help="Hostname or IP address")
    add_parser.add_argument("-u", "--user", help="SSH username")
    add_parser.add_argument("-p", "--port", type=int, default=22, help="SSH port (default: 22)")
    add_parser.add_argument("-i", "--identity", help="Identity file path")
    add_parser.add_argument("-d", "--description", help="Host description")
    add_parser.add_argument("-t", "--tags", help="Comma-separated tags")
    
    # Update command
    update_parser = subparsers.add_parser("update", help="Update existing host")
    update_parser.add_argument("name", help="Host name to update")
    update_parser.add_argument("--hostname", help="New hostname")
    update_parser.add_argument("--user", help="New username")
    update_parser.add_argument("--port", type=int, help="New port")
    update_parser.add_argument("--identity", help="New identity file")
    update_parser.add_argument("--description", help="New description")
    update_parser.add_argument("--tags", help="New comma-separated tags")
    
    # Remove command
    remove_parser = subparsers.add_parser("remove", help="Remove a host")
    remove_parser.add_argument("name", help="Host name to remove")
    
    # Show command
    show_parser = subparsers.add_parser("show", help="Show host details")
    show_parser.add_argument("name", help="Host name")
    
    # Connect command
    connect_parser = subparsers.add_parser("connect", help="Connect to a host")
    connect_parser.add_argument("name", help="Host name to connect")
    
    # Quick connect command
    quick_parser = subparsers.add_parser("quick", help="Quick connect without saving")
    quick_parser.add_argument("--host", required=True, help="Hostname or IP")
    quick_parser.add_argument("-u", "--user", help="Username")
    quick_parser.add_argument("-p", "--port", type=int, default=22, help="Port")
    
    # Test command
    test_parser = subparsers.add_parser("test", help="Test connection to host")
    test_parser.add_argument("name", help="Host name to test")
    
    # Suggest command
    suggest_parser = subparsers.add_parser("suggest", help="Get AI configuration suggestions")
    suggest_parser.add_argument("description", help="Server description")
    
    # History command
    history_parser = subparsers.add_parser("history", help="Show connection history")
    history_parser.add_argument("-l", "--limit", type=int, default=20, help="Number of entries")
    
    # Stats command
    subparsers.add_parser("stats", help="Show connection statistics")
    
    # Export command
    export_parser = subparsers.add_parser("export", help="Export configuration")
    export_parser.add_argument("file", help="Output file path")
    export_parser.add_argument("-f", "--format", choices=["json", "ssh_config"], 
                              default="json", help="Export format")
    
    # Import command
    import_parser = subparsers.add_parser("import", help="Import configuration")
    import_parser.add_argument("file", help="Input file path")
    import_parser.add_argument("-f", "--format", choices=["json", "ssh_config"],
                              default="json", help="Import format")
    
    args = parser.parse_args()
    
    # Initialize manager
    manager = SSHManager()
    
    # Handle commands
    if args.command is None:
        # No command - start interactive mode
        manager.interactive_shell()
    elif args.command == "list":
        manager.list_hosts()
    elif args.command == "add":
        tags = [t.strip() for t in args.tags.split(",")] if args.tags else None
        manager.add_host(args.name, args.host, args.user, args.port,
                        args.identity, args.description, tags)
    elif args.command == "update":
        tags = [t.strip() for t in args.tags.split(",")] if args.tags else None
        manager.update_host(args.name, hostname=args.hostname, user=args.user,
                          port=args.port, identity_file=args.identity,
                          description=args.description, tags=tags)
    elif args.command == "remove":
        manager.remove_host(args.name)
    elif args.command == "show":
        manager.show_host(args.name)
    elif args.command == "connect":
        manager.connect(args.name)
    elif args.command == "quick":
        manager.quick_connect(args.host, args.user, args.port)
    elif args.command == "test":
        manager.test_connection(args.name)
    elif args.command == "suggest":
        manager.ai_suggest(args.description)
    elif args.command == "history":
        manager.show_history(args.limit)
    elif args.command == "stats":
        manager.show_stats()
    elif args.command == "export":
        manager.export_config(args.file, args.format)
    elif args.command == "import":
        manager.import_config(args.file, args.format)


if __name__ == "__main__":
    main()
