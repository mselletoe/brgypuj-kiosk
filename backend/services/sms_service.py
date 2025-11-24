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
        # 1️⃣ Check environment variable
        env_port = os.getenv('SIM800L_PORT')
        if env_port:
            logger.info(f"Using port from environment: {env_port}")
            return env_port

        # 2️⃣ Check /dev/serial/by-id for Arduino/USB-Serial devices
        by_id_path = "/dev/serial/by-id/"
        if os.path.exists(by_id_path):
            for entry in os.listdir(by_id_path):
                if any(keyword in entry.lower() for keyword in ['arduino', 'usb']):
                    full_path = os.path.join(by_id_path, entry)
                    logger.info(f"Detected stable port: {full_path}")
                    return full_path

        # 3️⃣ Fallback: scan normal tty ports
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if any(keyword in port.description.lower() for keyword in 
                ['arduino', 'ch340', 'cp210', 'usb serial', 'ftdi', 'usb-serial']):
                logger.info(f"Auto-detected port: {port.device} ({port.description})")
                return port.device

        logger.warning("Could not auto-detect port. Please set SIM800L_PORT in .env")
        return None
    
    def _read_serial_thread(self):
        """Background thread to continuously read serial data"""
        while not self.stop_reading:
            try:
                if self.ser and self.ser.is_open and self.ser.in_waiting:
                    line = self.ser.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        logger.debug(f"Arduino → {line}")
                        with self.buffer_lock:
                            self.response_buffer.append(line)
                            # Keep buffer reasonable size
                            if len(self.response_buffer) > 100:
                                self.response_buffer.pop(0)
                time.sleep(0.01)
            except Exception as e:
                if not self.stop_reading:
                    logger.error(f"Error in read thread: {e}")
                break
    
    def connect(self) -> bool:
        """Establish connection with Arduino/SIM800L"""
        try:
            logger.info(f"Attempting to connect to {self.port}...")
            
            # Close existing connection if any
            if self.ser and self.ser.is_open:
                self.ser.close()
                time.sleep(0.5)
            
            # Open serial connection
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=1,
                write_timeout=1
            )
            
            logger.info("Serial port opened, waiting for Arduino reset...")
            time.sleep(3)  # Arduino resets on serial connection
            
            # Clear any garbage data
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()
            
            # Start background reader thread
            self.stop_reading = False
            with self.buffer_lock:
                self.response_buffer.clear()
            
            self.reader_thread = threading.Thread(target=self._read_serial_thread, daemon=True)
            self.reader_thread.start()
            
            # Test connection with PING
            logger.info("Testing connection with PING command...")
            test_result = self._send_command("PING", timeout=5.0)
            
            if test_result["status"] != "OK":
                logger.error(f"PING test failed: {test_result}")
                logger.error("Arduino is not responding. Please check:")
                logger.error("1. Arduino code is uploaded correctly")
                logger.error("2. Correct port (/dev/ttyACM0)")
                logger.error("3. Baud rate is 9600")
                logger.error("4. Arduino is powered and not frozen")
                return False
            
            logger.info("✓ Arduino responding to commands")
            
            # Wait for SYSTEM:READY or initialization messages
            start_time = time.time()
            system_ready = False
            
            while time.time() - start_time < 35:
                with self.buffer_lock:
                    for line in self.response_buffer:
                        if "SYSTEM:READY" in line:
                            system_ready = True
                            break
                        
                        if line.startswith("ERROR:"):
                            logger.warning(f"Arduino error during init: {line}")
                
                if system_ready:
                    break
                
                time.sleep(0.1)
            
            self.is_connected = True
            
            if system_ready:
                logger.info("✓ SIM800L module fully initialized")
            else:
                logger.warning("⚠ Arduino connected but didn't confirm full initialization")
                logger.info("Will attempt operations anyway...")
            
            # Try to get signal quality
            time.sleep(1)
            signal = self.get_signal_quality()
            if signal is not None:
                logger.info(f"📶 Signal Quality: {signal}/31")
            
            return True
                
        except serial.SerialException as e:
            logger.error(f"Serial connection error: {e}")
            logger.error("Possible causes:")
            logger.error("1. Wrong port - check with: ls /dev/ttyACM* /dev/ttyUSB*")
            logger.error(f"2. Permission denied - run: sudo chmod 666 {self.port}")
            logger.error("3. Port in use by another process")
            logger.error("4. Arduino not connected properly")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during connection: {e}")
            import traceback
            logger.error(traceback.format_exc())
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
            cmd_bytes = (command + '\n').encode('utf-8')
            self.ser.write(cmd_bytes)
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
                            return {"status": status, "message": message}
                        
                        if line.startswith("ERROR:"):
                            status = "ERROR"
                            message = line[6:] if len(line) > 6 else "Unknown error"
                            return {"status": status, "message": message}
                        
                        # For STATUS and SIGNAL commands
                        if line.startswith("STATUS:") or line.startswith("SIGNAL:"):
                            return {"status": "OK", "message": line}
                
                time.sleep(0.05)
            
            logger.warning(f"Command '{command}' timeout after {timeout}s")
            
            # Show what we did receive
            with self.buffer_lock:
                if self.response_buffer:
                    logger.warning(f"Received during timeout: {self.response_buffer}")
            
            return {"status": "ERROR", "message": "Command timeout"}
            
        except Exception as e:
            logger.error(f"Error sending command '{command}': {e}")
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
        # Auto-connect if not connected
        if not self.is_connected:
            logger.warning("Not connected, attempting to connect...")
            if not self.connect():
                return {"success": False, "message": "Failed to connect to SIM800L"}
        
        try:
            # Ensure phone number has + prefix
            if not phone_number.startswith('+'):
                phone_number = '+' + phone_number
            
            # Clean message (remove newlines, limit length)
            message = message.replace('\n', ' ').replace('\r', '')
            if len(message) > 160:
                message = message[:160]
                logger.warning("Message truncated to 160 characters")
            
            # Send command: SEND:<phone>:<message>
            command = f"SEND:{phone_number}:{message}"
            
            logger.info(f"📤 Sending SMS to {phone_number}")
            logger.debug(f"Message: {message}")
            
            # SMS can take 10-30 seconds
            response = self._send_command(command, timeout=45.0)
            
            if response["status"] == "OK":
                logger.info(f"✓ SMS sent successfully to {phone_number}")
                return {"success": True, "message": "SMS sent successfully"}
            else:
                error_msg = response.get("message", "Unknown error")
                logger.error(f"✗ SMS sending failed: {error_msg}")
                return {"success": False, "message": f"Failed to send SMS: {error_msg}"}
                
        except Exception as e:
            logger.error(f"Exception sending SMS: {e}")
            import traceback
            logger.error(traceback.format_exc())
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

# Auto-connect helper for lazy initialization
def ensure_connected():
    """Ensure service is connected, connect if needed"""
    if not sms_service.is_connected:
        return sms_service.connect()
    return True