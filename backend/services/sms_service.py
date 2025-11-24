import serial
import serial.tools.list_ports
import time
import logging
import os
from typing import Optional, Dict
import re
import threading

logger = logging.getLogger(__name__)

class SIM800LService:
    def __init__(self, port: str = None, baudrate: int = 9600):
        """
        Initialize SIM800L connection via Arduino
        
        Args:
            port: Serial port (auto-detect if None)
            baudrate: Communication speed (default 9600)
        """
        self.port = port or self._auto_detect_port()
        self.baudrate = baudrate
        self.ser = None
        self.is_connected = False
        self.last_signal = None
        self.response_buffer = []
        self.buffer_lock = threading.Lock()
        self.reader_thread = None
        self.stop_reading = False
        
    def _auto_detect_port(self) -> Optional[str]:
        """Auto-detect Arduino port"""
        env_port = os.getenv('SIM800L_PORT')
        if env_port:
            logger.info(f"Using port from environment: {env_port}")
            return env_port
        
        ports = serial.tools.list_ports.comports()
        
        for port in ports:
            if any(keyword in port.description.lower() for keyword in 
                   ['arduino', 'ch340', 'cp210', 'usb serial', 'ftdi', 'usb-serial']):
                logger.info(f"Auto-detected port: {port.device} ({port.description})")
                return port.device
        
        import platform
        system = platform.system()
        
        if system == 'Windows':
            default = 'COM5'
        elif system == 'Linux':
            if os.path.exists('/dev/ttyACM0'):
                default = '/dev/ttyACM0'
            elif os.path.exists('/dev/ttyUSB0'):
                default = '/dev/ttyUSB0'
            else:
                default = '/dev/ttyACM0'
        else:
            default = '/dev/tty.usbserial'
        
        logger.warning(f"Could not auto-detect port, using default: {default}")
        return default
    
    def _read_serial_thread(self):
        """Background thread to continuously read serial data"""
        while not self.stop_reading:
            try:
                if self.ser and self.ser.is_open and self.ser.in_waiting:
                    line = self.ser.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        logger.debug(f"Arduino: {line}")
                        with self.buffer_lock:
                            self.response_buffer.append(line)
                time.sleep(0.01)
            except Exception as e:
                if not self.stop_reading:
                    logger.error(f"Error in read thread: {e}")
                break
    
    def connect(self) -> bool:
        """Establish connection with Arduino/SIM800L"""
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
            time.sleep(2)  # Wait for Arduino to reset
            
            # Start background reader thread
            self.stop_reading = False
            self.reader_thread = threading.Thread(target=self._read_serial_thread, daemon=True)
            self.reader_thread.start()
            
            # Clear buffer
            with self.buffer_lock:
                self.response_buffer.clear()
            
            # Wait for SYSTEM:READY
            start_time = time.time()
            system_ready = False
            
            while time.time() - start_time < 10:
                with self.buffer_lock:
                    for line in self.response_buffer:
                        if line == "SYSTEM:READY":
                            system_ready = True
                            break
                        
                        if line.startswith("ERROR:"):
                            logger.error(f"Arduino reported error: {line}")
                            return False
                
                if system_ready:
                    break
                
                time.sleep(0.1)
            
            if system_ready:
                self.is_connected = True
                logger.info("✓ SIM800L module ready")
                
                # Try to read signal from buffer (non-blocking)
                with self.buffer_lock:
                    for line in self.response_buffer:
                        if line.startswith("SIGNAL:"):
                            match = re.search(r'SIGNAL:(\d+)', line)
                            if match:
                                self.last_signal = int(match.group(1))
                                logger.info(f"📶 Signal Quality: {self.last_signal}/31")
                                break
                
                return True
            else:
                # Even if we didn't get READY, assume it's connected if serial works
                self.is_connected = True
                logger.warning("Did not receive READY signal, but assuming connected")
                return True
                
        except serial.SerialException as e:
            logger.error(f"Serial connection error: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during connection: {e}")
            return False
    
    def disconnect(self):
        """Close serial connection"""
        self.stop_reading = True
        if self.reader_thread:
            self.reader_thread.join(timeout=2)
        
        if self.ser and self.ser.is_open:
            self.ser.close()
            self.is_connected = False
            logger.info("SIM800L disconnected")
    
    def _send_command(self, command: str, timeout: float = 5.0) -> Dict[str, str]:
        """
        Send command to Arduino and wait for response
        
        Returns:
            dict with 'status' and 'message'
        """
        if not self.ser or not self.ser.is_open:
            return {"status": "ERROR", "message": "Serial not connected"}
        
        try:
            # Clear previous responses
            with self.buffer_lock:
                self.response_buffer.clear()
            
            # Send command
            self.ser.write((command + '\n').encode())
            self.ser.flush()
            logger.debug(f"→ Sent: {command}")
            
            # Wait for response
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                with self.buffer_lock:
                    for line in self.response_buffer:
                        logger.debug(f"← Received: {line}")
                        
                        # Look for completion responses
                        if line.startswith("OK:"):
                            status = "OK"
                            message = line[3:] if len(line) > 3 else ""
                            logger.info(f"✓ Command success: {message}")
                            return {"status": status, "message": message}
                        
                        if line.startswith("ERROR:"):
                            status = "ERROR"
                            message = line[6:] if len(line) > 6 else "Unknown error"
                            logger.error(f"✗ Command failed: {message}")
                            return {"status": status, "message": message}
                        
                        # For STATUS and SIGNAL commands
                        if line.startswith("STATUS:") or line.startswith("SIGNAL:"):
                            return {"status": "OK", "message": line}
                
                time.sleep(0.05)
            
            logger.warning(f"Command timeout after {timeout}s")
            return {"status": "ERROR", "message": "Command timeout"}
            
        except Exception as e:
            logger.error(f"Error sending command: {e}")
            return {"status": "ERROR", "message": str(e)}
    
    def send_sms(self, phone_number: str, message: str) -> dict:
        """
        Send SMS message via Arduino/SIM800L
        
        Args:
            phone_number: Recipient phone number (e.g., '+639123456789')
            message: SMS message content
            
        Returns:
            dict with success status and message
        """
        if not self.is_connected:
            return {"success": False, "message": "SIM800L not connected"}
        
        try:
            # Ensure phone number has + prefix
            if not phone_number.startswith('+'):
                phone_number = '+' + phone_number
            
            # Clean message
            message = message.replace('\n', ' ').replace('\r', '')
            
            # Send command: SEND:<phone>:<message>
            command = f"SEND:{phone_number}:{message}"
            
            logger.info(f"📤 Sending SMS to {phone_number}")
            logger.debug(f"Message: {message}")
            
            # SMS can take 10-30 seconds
            response = self._send_command(command, timeout=40.0)
            
            if response["status"] == "OK":
                logger.info(f"✓ SMS sent successfully to {phone_number}")
                return {"success": True, "message": "SMS sent successfully"}
            else:
                error_msg = response.get("message", "Unknown error")
                logger.error(f"✗ SMS sending failed: {error_msg}")
                return {"success": False, "message": f"Failed to send SMS: {error_msg}"}
                
        except Exception as e:
            logger.error(f"Exception sending SMS: {e}")
            return {"success": False, "message": str(e)}
    
    def get_signal_quality(self) -> Optional[int]:
        """Get signal strength (0-31, 99=unknown)"""
        if not self.is_connected:
            return None
        
        try:
            response = self._send_command("SIGNAL", timeout=3.0)
            
            if response["status"] == "OK" and "message" in response:
                # Extract number from "SIGNAL:18"
                match = re.search(r'SIGNAL:(\d+)', response["message"])
                if match:
                    signal = int(match.group(1))
                    self.last_signal = signal
                    return signal
            
            return self.last_signal
            
        except Exception as e:
            logger.error(f"Error getting signal quality: {e}")
            return None
    
    def _update_signal_quality(self):
        """Update cached signal quality"""
        self.get_signal_quality()
    
    def get_status(self) -> Dict[str, any]:
        """Get module status"""
        if not self.is_connected:
            return {"connected": False}
        
        signal = self.get_signal_quality()
        
        return {
            "connected": True,
            "port": self.port,
            "signal_quality": signal,
            "signal_bars": min(5, (signal // 6)) if signal else 0
        }

# Global instance
sms_service = SIM800LService()