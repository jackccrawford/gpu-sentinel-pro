import subprocess
import shutil
import logging
from typing import Dict, List, Optional
import re
import os

logger = logging.getLogger(__name__)

class SystemHealthCheck:
    def __init__(self):
        # Find nvidia-smi with full path and validate it
        self.nvidia_smi_path = shutil.which('nvidia-smi')
        if self.nvidia_smi_path:
            self.nvidia_smi_path = os.path.realpath(self.nvidia_smi_path)
            if not os.path.exists(self.nvidia_smi_path):
                self.nvidia_smi_path = None
            elif not os.access(self.nvidia_smi_path, os.X_OK):
                self.nvidia_smi_path = None
        self._driver_version = None
        self._cuda_version = None

    def _validate_nvidia_command(self, args: List[str]) -> bool:
        """Validate nvidia-smi command arguments"""
        valid_args = [
            "--query-gpu=gpu_name",
            "--query-gpu=gpu_name,gpu_bus_id,memory.total,compute_mode",
            "--query-gpu=driver_version",
            "--query-gpu=index,name,fan.speed,power.draw,memory.total,memory.used,utilization.gpu,temperature.gpu,compute_mode,power.limit",
            "--format=csv,noheader",
            "--format=csv,noheader,nounits"
        ]
        return all(arg in valid_args or arg == self.nvidia_smi_path for arg in args)

    def _run_nvidia_command(self, args: List[str]) -> subprocess.CompletedProcess:
        """Run nvidia-smi command with validation"""
        if not self.nvidia_smi_path:
            raise RuntimeError("nvidia-smi not found or not executable")
        
        if not self._validate_nvidia_command(args):
            raise ValueError("Invalid nvidia-smi arguments")

        return subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=5,
            check=False  # We handle return code manually
        )

    def check_nvidia_smi(self) -> Dict[str, bool | str]:
        """Check if nvidia-smi is available and accessible."""
        if not self.nvidia_smi_path:
            logger.error("nvidia-smi not found in system PATH")
            return {
                "available": False,
                "error": "NVIDIA System Management Interface (nvidia-smi) not found. Please install NVIDIA drivers."
            }
        
        try:
            result = self._run_nvidia_command([
                self.nvidia_smi_path,
                "--query-gpu=gpu_name",
                "--format=csv,noheader"
            ])
            if result.returncode != 0:
                logger.error(f"nvidia-smi command failed: {result.stderr}")
                return {
                    "available": False,
                    "error": f"nvidia-smi command failed: {result.stderr}"
                }
            return {"available": True, "path": self.nvidia_smi_path}
        except subprocess.TimeoutExpired:
            logger.error("nvidia-smi command timed out")
            return {
                "available": False,
                "error": "nvidia-smi command timed out. System might be overloaded."
            }
        except Exception as e:
            logger.error(f"Error running nvidia-smi: {str(e)}")
            return {
                "available": False,
                "error": f"Error running nvidia-smi: {str(e)}"
            }

    def check_gpus(self) -> Dict[str, bool | List[str] | str]:
        """Check for available GPUs and their status."""
        if not self.nvidia_smi_path:
            return {
                "available": False,
                "error": "nvidia-smi not available",
                "gpus": []
            }

        try:
            result = self._run_nvidia_command([
                self.nvidia_smi_path,
                "--query-gpu=gpu_name,gpu_bus_id,memory.total,compute_mode",
                "--format=csv,noheader"
            ])
            
            if result.returncode != 0:
                return {
                    "available": False,
                    "error": f"GPU query failed: {result.stderr}",
                    "gpus": []
                }

            gpus = [gpu.strip() for gpu in result.stdout.split('\n') if gpu.strip()]
            
            if not gpus:
                return {
                    "available": False,
                    "error": "No GPUs detected",
                    "gpus": []
                }

            return {
                "available": True,
                "count": len(gpus),
                "gpus": gpus
            }

        except Exception as e:
            logger.error(f"Error checking GPUs: {str(e)}")
            return {
                "available": False,
                "error": f"Error checking GPUs: {str(e)}",
                "gpus": []
            }

    def check_driver_version(self) -> Dict[str, bool | str]:
        """Check NVIDIA driver version."""
        if not self.nvidia_smi_path:
            return {
                "available": False,
                "error": "nvidia-smi not available"
            }

        try:
            result = self._run_nvidia_command([
                self.nvidia_smi_path,
                "--query-gpu=driver_version",
                "--format=csv,noheader"
            ])
            
            if result.returncode != 0:
                return {
                    "available": False,
                    "error": f"Driver version query failed: {result.stderr}"
                }

            version = result.stdout.strip()
            if not version:
                return {
                    "available": False,
                    "error": "Could not determine driver version"
                }

            self._driver_version = version
            return {
                "available": True,
                "version": version
            }

        except Exception as e:
            logger.error(f"Error checking driver version: {str(e)}")
            return {
                "available": False,
                "error": f"Error checking driver version: {str(e)}"
            }

    def check_cuda_version(self) -> Dict[str, bool | str]:
        """Check CUDA version."""
        if not self.nvidia_smi_path:
            return {
                "available": False,
                "error": "nvidia-smi not available"
            }

        try:
            result = self._run_nvidia_command([self.nvidia_smi_path])
            
            if result.returncode != 0:
                return {
                    "available": False,
                    "error": f"CUDA version query failed: {result.stderr}"
                }

            # Look for CUDA Version in output
            cuda_match = re.search(r'CUDA Version:\s+(\d+\.\d+)', result.stdout)
            if not cuda_match:
                return {
                    "available": False,
                    "error": "Could not determine CUDA version"
                }

            self._cuda_version = cuda_match.group(1)
            return {
                "available": True,
                "version": self._cuda_version
            }

        except Exception as e:
            logger.error(f"Error checking CUDA version: {str(e)}")
            return {
                "available": False,
                "error": f"Error checking CUDA version: {str(e)}"
            }

    def check_memory_requirements(self) -> Dict[str, bool | str]:
        """Check if system meets memory requirements."""
        try:
            import psutil
            memory = psutil.virtual_memory()
            
            # Require at least 4GB of total RAM
            min_memory = 4 * 1024 * 1024 * 1024  # 4GB in bytes
            
            if memory.total < min_memory:
                return {
                    "meets_requirements": False,
                    "error": f"Insufficient system memory. Required: 4GB, Available: {memory.total / (1024**3):.1f}GB"
                }
                
            return {
                "meets_requirements": True,
                "total_memory": f"{memory.total / (1024**3):.1f}GB",
                "available_memory": f"{memory.available / (1024**3):.1f}GB"
            }
            
        except Exception as e:
            logger.error(f"Error checking system memory: {str(e)}")
            return {
                "meets_requirements": False,
                "error": f"Error checking system memory: {str(e)}"
            }

    def run_full_check(self) -> Dict[str, any]:
        """Run all system health checks."""
        return {
            "nvidia_smi": self.check_nvidia_smi(),
            "gpus": self.check_gpus(),
            "driver": self.check_driver_version(),
            "cuda": self.check_cuda_version(),
            "memory": self.check_memory_requirements(),
            "system_ready": all([
                self.check_nvidia_smi().get("available", False),
                self.check_gpus().get("available", False),
                self.check_driver_version().get("available", False),
                self.check_cuda_version().get("available", False),
                self.check_memory_requirements().get("meets_requirements", False)
            ])
        }

    def get_user_friendly_message(self, check_results: Dict[str, any]) -> str:
        """Generate a user-friendly message from check results."""
        if check_results["system_ready"]:
            return "System is ready for GPU monitoring."

        messages = []
        
        if not check_results["nvidia_smi"]["available"]:
            messages.append(f"NVIDIA SMI Issue: {check_results['nvidia_smi']['error']}")
        
        if not check_results["gpus"]["available"]:
            messages.append(f"GPU Issue: {check_results['gpus']['error']}")
        
        if not check_results["driver"]["available"]:
            messages.append(f"Driver Issue: {check_results['driver']['error']}")
        
        if not check_results["cuda"]["available"]:
            messages.append(f"CUDA Issue: {check_results['cuda']['error']}")
        
        if not check_results["memory"]["meets_requirements"]:
            messages.append(f"Memory Issue: {check_results['memory']['error']}")

        return "\n".join(messages)

# Example usage:
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    health_check = SystemHealthCheck()
    results = health_check.run_full_check()
    print(health_check.get_user_friendly_message(results))