#!/usr/bin/env python3
"""
Enhanced ChromaDB Robustness and Recovery System
Provides comprehensive safeguards against corruption and automatic recovery
"""

import os
import json
import time
import shutil
import logging
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from threading import Lock
import chromadb
from chromadb.config import Settings as ChromaSettings

logger = logging.getLogger(__name__)

class ChromaDBRobustnessManager:
    """Enhanced ChromaDB manager with corruption prevention and recovery"""
    
    def __init__(self, chroma_path: str):
        self.chroma_path = Path(chroma_path)
        self.backup_path = self.chroma_path.parent / "chroma_backups"
        self.metadata_file = self.chroma_path.parent / "chroma_metadata.json"
        self.lock = Lock()
        
        # Create directories
        self.chroma_path.mkdir(exist_ok=True, parents=True)
        self.backup_path.mkdir(exist_ok=True, parents=True)
        
        # Health check settings
        self.last_health_check = None
        self.health_check_interval = timedelta(minutes=5)
        self.max_backup_count = 10
        
        # Initialize metadata
        self._init_metadata()
    
    def _init_metadata(self):
        """Initialize metadata tracking file"""
        if not self.metadata_file.exists():
            metadata = {
                "created": datetime.now().isoformat(),
                "last_backup": None,
                "last_health_check": None,
                "corruption_events": [],
                "recovery_events": [],
                "document_count": 0,
                "collection_info": {}
            }
            self._save_metadata(metadata)
    
    def _load_metadata(self) -> Dict:
        """Load metadata from file"""
        try:
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load metadata: {e}")
            self._init_metadata()
            return self._load_metadata()
    
    def _save_metadata(self, metadata: Dict):
        """Save metadata to file"""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save metadata: {e}")
    
    def create_backup(self, reason: str = "manual") -> Optional[str]:
        """Create a backup of ChromaDB"""
        try:
            with self.lock:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_dir = self.backup_path / f"backup_{timestamp}_{reason}"
                
                if self.chroma_path.exists():
                    shutil.copytree(self.chroma_path, backup_dir)
                    
                    # Update metadata
                    metadata = self._load_metadata()
                    metadata["last_backup"] = datetime.now().isoformat()
                    metadata["recovery_events"].append({
                        "timestamp": datetime.now().isoformat(),
                        "action": "backup_created",
                        "reason": reason,
                        "backup_path": str(backup_dir)
                    })
                    self._save_metadata(metadata)
                    
                    # Cleanup old backups
                    self._cleanup_old_backups()
                    
                    logger.info(f"Backup created: {backup_dir}")
                    return str(backup_dir)
                else:
                    logger.warning("ChromaDB directory does not exist, cannot create backup")
                    return None
                    
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return None
    
    def _cleanup_old_backups(self):
        """Remove old backups, keeping only the most recent ones"""
        try:
            backups = sorted([
                d for d in self.backup_path.iterdir() 
                if d.is_dir() and d.name.startswith("backup_")
            ], key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Keep only the most recent backups
            for old_backup in backups[self.max_backup_count:]:
                shutil.rmtree(old_backup)
                logger.info(f"Removed old backup: {old_backup}")
                
        except Exception as e:
            logger.warning(f"Failed to cleanup old backups: {e}")
    
    def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        health_status = {
            "timestamp": datetime.now().isoformat(),
            "healthy": True,
            "issues": [],
            "warnings": [],
            "stats": {}
        }
        
        try:
            # Check if ChromaDB directory exists and is accessible
            if not self.chroma_path.exists():
                health_status["issues"].append("ChromaDB directory does not exist")
                health_status["healthy"] = False
                return health_status
            
            # Check directory permissions
            if not os.access(self.chroma_path, os.R_OK | os.W_OK):
                health_status["issues"].append("ChromaDB directory not readable/writable")
                health_status["healthy"] = False
            
            # Check for empty or corrupted index files
            corrupted_files = []
            for file_path in self.chroma_path.rglob("*"):
                if file_path.is_file():
                    if file_path.stat().st_size == 0:
                        corrupted_files.append(str(file_path))
            
            if corrupted_files:
                health_status["warnings"].append(f"Found {len(corrupted_files)} empty files")
                health_status["stats"]["empty_files"] = corrupted_files
            
            # Try to connect to ChromaDB
            try:
                client = chromadb.PersistentClient(
                    path=str(self.chroma_path),
                    settings=ChromaSettings(
                        anonymized_telemetry=False,
                        allow_reset=True,
                        is_persistent=True
                    )
                )
                
                # Try to list collections
                collections = client.list_collections()
                health_status["stats"]["collections_count"] = len(collections)
                
                # Check main collection if it exists
                try:
                    collection = client.get_collection("knowledge_base_collection")
                    count = collection.count()
                    health_status["stats"]["document_count"] = count
                    
                    # Try a simple query to test functionality
                    if count > 0:
                        try:
                            results = collection.query(
                                query_texts=["test query"],
                                n_results=1,
                                include=["documents", "metadatas"]
                            )
                            health_status["stats"]["query_test"] = "success"
                        except Exception as e:
                            health_status["issues"].append(f"Query test failed: {e}")
                            health_status["healthy"] = False
                            
                except Exception as e:
                    health_status["warnings"].append(f"Collection access issue: {e}")
                    
            except Exception as e:
                health_status["issues"].append(f"ChromaDB connection failed: {e}")
                health_status["healthy"] = False
            
            # Update metadata
            metadata = self._load_metadata()
            metadata["last_health_check"] = health_status["timestamp"]
            if not health_status["healthy"]:
                metadata["corruption_events"].append(health_status)
            self._save_metadata(metadata)
            
            self.last_health_check = datetime.now()
            
        except Exception as e:
            health_status["issues"].append(f"Health check failed: {e}")
            health_status["healthy"] = False
        
        return health_status
    
    def auto_recovery(self, corruption_type: str = "general") -> bool:
        """Attempt automatic recovery from corruption"""
        try:
            logger.warning(f"Starting auto-recovery for: {corruption_type}")
            
            # Create backup of current state (even if corrupted)
            backup_path = self.create_backup(f"pre_recovery_{corruption_type}")
            
            recovery_success = False
            
            if corruption_type == "empty_files":
                recovery_success = self._recover_from_empty_files()
            elif corruption_type == "connection_failure":
                recovery_success = self._recover_from_connection_failure()
            elif corruption_type == "index_corruption":
                recovery_success = self._recover_from_index_corruption()
            else:
                # General recovery: clean slate
                recovery_success = self._full_reset_recovery()
            
            # Update metadata
            metadata = self._load_metadata()
            metadata["recovery_events"].append({
                "timestamp": datetime.now().isoformat(),
                "corruption_type": corruption_type,
                "success": recovery_success,
                "backup_created": backup_path
            })
            self._save_metadata(metadata)
            
            if recovery_success:
                logger.info(f"Auto-recovery successful for: {corruption_type}")
            else:
                logger.error(f"Auto-recovery failed for: {corruption_type}")
            
            return recovery_success
            
        except Exception as e:
            logger.error(f"Auto-recovery failed with exception: {e}")
            return False
    
    def _recover_from_empty_files(self) -> bool:
        """Recover from empty/corrupted index files"""
        try:
            # Remove empty files
            for file_path in self.chroma_path.rglob("*"):
                if file_path.is_file() and file_path.stat().st_size == 0:
                    file_path.unlink()
                    logger.info(f"Removed empty file: {file_path}")
            
            return True
        except Exception as e:
            logger.error(f"Failed to recover from empty files: {e}")
            return False
    
    def _recover_from_connection_failure(self) -> bool:
        """Recover from ChromaDB connection failures"""
        try:
            # Try to reinitialize ChromaDB with fresh settings
            if self.chroma_path.exists():
                # Remove potentially corrupted sqlite files
                for sqlite_file in self.chroma_path.rglob("*.sqlite*"):
                    try:
                        sqlite_file.unlink()
                        logger.info(f"Removed potentially corrupted SQLite file: {sqlite_file}")
                    except Exception as e:
                        logger.warning(f"Could not remove {sqlite_file}: {e}")
            
            return True
        except Exception as e:
            logger.error(f"Failed to recover from connection failure: {e}")
            return False
    
    def _recover_from_index_corruption(self) -> bool:
        """Recover from index corruption"""
        try:
            # Remove index-related files
            for index_file in self.chroma_path.rglob("*.bin"):
                try:
                    index_file.unlink()
                    logger.info(f"Removed corrupted index file: {index_file}")
                except Exception as e:
                    logger.warning(f"Could not remove {index_file}: {e}")
            
            return True
        except Exception as e:
            logger.error(f"Failed to recover from index corruption: {e}")
            return False
    
    def _full_reset_recovery(self) -> bool:
        """Perform full reset recovery"""
        try:
            # Remove entire ChromaDB directory and recreate
            if self.chroma_path.exists():
                shutil.rmtree(self.chroma_path)
            
            self.chroma_path.mkdir(exist_ok=True, parents=True)
            logger.info("Performed full ChromaDB reset")
            
            return True
        except Exception as e:
            logger.error(f"Failed to perform full reset: {e}")
            return False
    
    def restore_from_backup(self, backup_name: Optional[str] = None) -> bool:
        """Restore ChromaDB from backup"""
        try:
            if backup_name:
                backup_dir = self.backup_path / backup_name
            else:
                # Use most recent backup
                backups = sorted([
                    d for d in self.backup_path.iterdir() 
                    if d.is_dir() and d.name.startswith("backup_")
                ], key=lambda x: x.stat().st_mtime, reverse=True)
                
                if not backups:
                    logger.error("No backups available for restore")
                    return False
                
                backup_dir = backups[0]
            
            if not backup_dir.exists():
                logger.error(f"Backup directory not found: {backup_dir}")
                return False
            
            # Create backup of current state before restore
            self.create_backup("pre_restore")
            
            # Remove current ChromaDB
            if self.chroma_path.exists():
                shutil.rmtree(self.chroma_path)
            
            # Restore from backup
            shutil.copytree(backup_dir, self.chroma_path)
            
            logger.info(f"Restored ChromaDB from backup: {backup_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore from backup: {e}")
            return False
    
    def get_status_report(self) -> Dict[str, Any]:
        """Get comprehensive status report"""
        try:
            metadata = self._load_metadata()
            health = self.health_check()
            
            # Get backup info
            backups = []
            if self.backup_path.exists():
                for backup_dir in self.backup_path.iterdir():
                    if backup_dir.is_dir() and backup_dir.name.startswith("backup_"):
                        backups.append({
                            "name": backup_dir.name,
                            "created": datetime.fromtimestamp(backup_dir.stat().st_mtime).isoformat(),
                            "size_mb": sum(f.stat().st_size for f in backup_dir.rglob('*') if f.is_file()) / (1024*1024)
                        })
            
            backups.sort(key=lambda x: x["created"], reverse=True)
            
            return {
                "chroma_path": str(self.chroma_path),
                "metadata": metadata,
                "health": health,
                "backups": backups[:5],  # Last 5 backups
                "recommendations": self._get_recommendations(health, metadata)
            }
            
        except Exception as e:
            logger.error(f"Failed to generate status report: {e}")
            return {"error": str(e)}
    
    def _get_recommendations(self, health: Dict, metadata: Dict) -> List[str]:
        """Generate recommendations based on system status"""
        recommendations = []
        
        if not health["healthy"]:
            recommendations.append("Run auto-recovery to fix detected issues")
        
        if health.get("warnings"):
            recommendations.append("Monitor warnings and consider preventive backup")
        
        if metadata.get("last_backup"):
            last_backup = datetime.fromisoformat(metadata["last_backup"])
            if datetime.now() - last_backup > timedelta(days=1):
                recommendations.append("Create fresh backup (last backup > 24 hours old)")
        else:
            recommendations.append("Create initial backup")
        
        corruption_events = metadata.get("corruption_events", [])
        if len(corruption_events) > 3:
            recommendations.append("Frequent corruption detected - consider investigating underlying cause")
        
        return recommendations

def create_robustness_manager(chroma_path: str) -> ChromaDBRobustnessManager:
    """Factory function to create robustness manager"""
    return ChromaDBRobustnessManager(chroma_path)

# Example usage and testing
if __name__ == "__main__":
    # Test the robustness manager
    manager = ChromaDBRobustnessManager("/app/chroma_db")
    
    print("=== ChromaDB Robustness Manager Test ===")
    
    # Perform health check
    health = manager.health_check()
    print(f"Health Check: {'HEALTHY' if health['healthy'] else 'ISSUES DETECTED'}")
    
    # Create backup
    backup_path = manager.create_backup("test")
    print(f"Backup created: {backup_path}")
    
    # Get status report
    status = manager.get_status_report()
    print(f"Status Report Generated: {len(status)} sections")
    
    print("=== Test Complete ===")