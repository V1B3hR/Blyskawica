# Cameras Module - IR Night Vision 🌙

## 🎯 Overview

The Cameras module implements **Fala 2: Kamery na Podczerwień** (Wave 2: IR Cameras) from the Nethical Hunter 3.0 roadmap. These are specialized reconnaissance tools that provide "Deep/Dark Discovery" capabilities - seeing what normal sensors cannot detect.

> *"Nie ważne jak się ukryjesz - znajdę Cię w nocy, w dzień i przy złej pogodzie"*  
> *"No matter how you hide - I'll find you at night, day, and in bad weather"*

## 🔭 Camera Types

Each camera has a specialized "vision mode" for different reconnaissance tasks:

### 🌙 Night Vision - Shodan/Censys
**Cameras:** `ShodanEye`, `CensysEye`  
**Mode:** `NIGHT`  
**Sees:** Hidden services in the darkness of the Internet
- Internet-exposed devices and services
- Open ports and banners
- SSL certificates
- Known vulnerabilities
- Geographic locations

### 🌧️ Bad Weather - theHarvester
**Camera:** `HarvesterEye`  
**Mode:** `BAD_WEATHER`  
**Sees:** OSINT data through the fog
- Email addresses
- Subdomains
- Hosts and IPs
- Employee names
- Social media profiles

### 👻 Ghost Vision - DNS Enumeration
**Camera:** `DNSEnumerator`  
**Mode:** `GHOST`  
**Sees:** Invisible subdomains and DNS records
- Subdomains (brute-force and DNS walking)
- All DNS record types (A, AAAA, MX, NS, TXT, etc.)
- Zone transfer attempts
- DNSSEC configuration

### 🕳️ X-ray Vision - SSL/TLS Analysis
**Camera:** `SSLScanner`  
**Mode:** `XRAY`  
**Sees:** Through encryption layers
- Certificate details
- Cipher suites and protocols
- Weak configurations
- Expired certificates
- Self-signed certificates

### 🎭 Mask Detection - WAF Discovery
**Camera:** `WAFDetector`  
**Mode:** `MASK`  
**Sees:** Hidden security defenses
- Web Application Firewalls (Cloudflare, AWS WAF, Akamai, etc.)
- Security headers
- Protection mechanisms
- Block patterns

## 📦 Installation

### Basic Installation
```bash
pip install -r requirements.txt
```

### Individual Camera Requirements

#### Shodan Eye
```bash
pip install shodan
export SHODAN_API_KEY="your_api_key"
```

#### Censys Eye
```bash
pip install censys
export CENSYS_API_ID="your_api_id"
export CENSYS_API_SECRET="your_api_secret"
```

#### Harvester Eye
```bash
# Install theHarvester system tool
sudo apt-get install theharvester  # Debian/Ubuntu
# or
git clone https://github.com/laramies/theHarvester.git
cd theHarvester
pip install -r requirements.txt
```

#### DNS Enumerator
```bash
pip install dnspython
```

#### SSL Scanner
```bash
# Uses Python standard library - no additional install needed
```

#### WAF Detector
```bash
pip install requests urllib3
```

## 🚀 Quick Start

### Basic Usage

```python
from cameras import CameraManager, ShodanEye, DNSEnumerator, SSLScanner

# Create camera manager
manager = CameraManager()

# Register cameras
shodan = ShodanEye(config={'api_key': 'your_key'})
dns = DNSEnumerator()
ssl = SSLScanner()

manager.register_camera(shodan)
manager.register_camera(dns)
manager.register_camera(ssl)

# Scan a target
results = manager.scan_with_camera('ShodanEye', '8.8.8.8')
print(results)

# Or scan with all cameras
all_results = manager.scan_all('example.com', async_mode=True)
```

### Individual Camera Usage

#### Shodan Eye Example
```python
from cameras import ShodanEye

# Initialize
camera = ShodanEye(config={'api_key': 'YOUR_API_KEY'})

# Scan an IP
results = camera.scan('8.8.8.8')
print(f"Found {len(results['host_info']['services'])} services")

# Search for exposed services
results = camera.scan('apache country:US')
```

#### DNS Enumerator Example
```python
from cameras import DNSEnumerator

# Initialize
camera = DNSEnumerator(config={
    'check_zone_transfer': True
})

# Enumerate DNS
results = camera.scan('example.com')
print(f"Found {len(results['subdomains'])} subdomains")
print(f"Nameservers: {results['nameservers']}")
```

#### SSL Scanner Example
```python
from cameras import SSLScanner

# Initialize
camera = SSLScanner(config={'ports': [443, 8443]})

# Scan SSL/TLS
results = camera.scan('example.com')
print(f"Found {len(results['vulnerabilities'])} vulnerabilities")
```

#### WAF Detector Example
```python
from cameras import WAFDetector

# Initialize
camera = WAFDetector()

# Detect WAF
results = camera.scan('https://example.com')
if results['waf_detected']:
    print(f"WAF detected: {results['waf_name']} ({results['confidence']:.0%} confidence)")
```

## 🎨 Camera Manager Features

### Scan Operations
```python
from cameras import CameraManager

manager = CameraManager()

# Register multiple cameras
manager.register_camera(shodan_cam)
manager.register_camera(dns_cam)
manager.register_camera(ssl_cam)

# Scan with specific camera
result = manager.scan_with_camera('ShodanEye', 'target.com')

# Scan with all cameras (parallel)
results = manager.scan_all('target.com', async_mode=True)

# Stop specific camera
manager.stop_camera('ShodanEye')

# Stop all cameras
manager.stop_all()
```

### Discovery Management
```python
# Get all discoveries
discoveries = manager.get_all_discoveries()

# Filter by severity
critical = manager.get_all_discoveries(severity='CRITICAL')

# Get discoveries from specific camera
shodan_disc = manager.get_discoveries_by_camera('ShodanEye')

# Clear all discoveries
manager.clear_all_discoveries()
```

### Statistics
```python
# Get aggregated statistics
stats = manager.get_statistics()
print(f"Total discoveries: {stats['total_discoveries']}")
print(f"By camera: {stats['by_camera']}")
print(f"By severity: {stats['by_severity']}")
```

## 🔧 Configuration

### Camera Configuration Options

#### ShodanEye
```python
config = {
    'api_key': 'YOUR_KEY',  # Or set SHODAN_API_KEY env var
    'max_results': 100
}
```

#### CensysEye
```python
config = {
    'api_id': 'YOUR_ID',       # Or set CENSYS_API_ID env var
    'api_secret': 'YOUR_SECRET', # Or set CENSYS_API_SECRET env var
    'max_results': 100
}
```

#### HarvesterEye
```python
config = {
    'sources': ['google', 'bing', 'duckduckgo'],
    'limit': 500,
    'timeout': 120
}
```

#### DNSEnumerator
```python
config = {
    'wordlist': '/path/to/subdomains.txt',  # Optional
    'nameservers': [],  # Use custom nameservers
    'timeout': 2,
    'check_zone_transfer': True
}
```

#### SSLScanner
```python
config = {
    'ports': [443, 8443, 8080],
    'timeout': 5,
    'check_vulnerabilities': True
}
```

#### WAFDetector
```python
config = {
    'timeout': 10,
    'user_agent': 'Nethical/2.0',
    'test_payloads': True,
    'verify_ssl': False  # SSL verification (False by default for recon)
}
```

**Note on SSL Verification**: By default, `verify_ssl` is set to `False` for reconnaissance purposes to allow scanning of targets with self-signed or invalid certificates. This is intentional for security testing but can be enabled if needed: `config={'verify_ssl': True}`.

## 📊 Discovery Types

Cameras record different types of discoveries:

| Discovery Type | Description | Cameras |
|---------------|-------------|----------|
| `service` | Exposed service/port | Shodan, Censys |
| `vulnerability` | Security vulnerability | Shodan, SSL Scanner, DNS |
| `subdomain` | Discovered subdomain | Harvester, DNS |
| `email` | Email address | Harvester |
| `ssl_certificate` | SSL/TLS certificate | SSL Scanner |
| `dns_record` | DNS record | DNS Enumerator |
| `waf` | Web Application Firewall | WAF Detector |
| `exposed_service` | Publicly exposed service | Shodan, Censys |
| `certificate` | Certificate details | Censys |

## 🛡️ Security Considerations

⚠️ **Important:**

1. **Authorization Required**: Only scan systems you own or have explicit permission to test
2. **API Keys**: Keep API keys secure - use environment variables
3. **Rate Limiting**: Respect API rate limits (especially Shodan/Censys)
4. **Legal Compliance**: Unauthorized scanning may be illegal in your jurisdiction
5. **Privacy**: Be mindful of privacy when collecting email addresses and personal data
6. **SSL/TLS Verification**: 
   - WAF Detector: SSL verification is disabled by default for reconnaissance but can be enabled via `verify_ssl` config
   - SSL Scanner: Intentionally connects to servers with weak SSL/TLS configurations (including old protocols like TLSv1) to identify and report vulnerabilities. This is necessary for security testing.

### About SSL Scanner Security

The SSL Scanner is designed as a **security analysis tool** that needs to connect to servers with weak or outdated SSL/TLS configurations. It intentionally:
- Allows old protocol versions (TLSv1, TLSv1.1) to detect servers still using them
- Disables certificate verification to analyze self-signed or expired certificates
- Accepts weak ciphers to identify them as vulnerabilities

This behavior is **correct and intended** for a reconnaissance tool. The scanner reports these configurations as security vulnerabilities, which is its purpose.

## 🔍 Advanced Usage

### Custom Camera Development

Create your own camera by extending `BaseCamera`:

```python
from cameras.base import BaseCamera, CameraMode

class MyCustomCamera(BaseCamera):
    def __init__(self, config=None):
        super().__init__("MyCamera", CameraMode.NIGHT, config)
    
    def scan(self, target: str) -> dict:
        # Implement your scanning logic
        results = {'target': target, 'data': []}
        
        # Record discoveries
        self.record_discovery(
            'custom_type',
            target,
            {'info': 'discovered data'},
            confidence=0.95,
            severity='INFO'
        )
        
        return results
```

### Chaining Cameras

Use discoveries from one camera to feed another:

```python
# Discover subdomains
dns_results = dns_cam.scan('example.com')

# Scan SSL on discovered subdomains
for subdomain in dns_results['subdomains']:
    ssl_cam.scan(subdomain)
```

## 📈 Performance Tips

1. **Use async_mode** for parallel scanning: `manager.scan_all(target, async_mode=True)`
2. **Limit results** in API-based cameras to avoid timeouts
3. **Use wordlists** efficiently - start with common subdomains
4. **Cache results** for repeated scans
5. **Respect rate limits** to avoid being blocked

## 🐛 Troubleshooting

### Common Issues

**Shodan/Censys API Errors:**
```bash
# Check if API key is set
echo $SHODAN_API_KEY
# or
echo $CENSYS_API_ID

# Test API key
python -c "import shodan; api = shodan.Shodan('YOUR_KEY'); print(api.info())"
```

**theHarvester Not Found:**
```bash
which theHarvester
# If not found, install it:
sudo apt-get install theharvester
```

**DNS Timeout Issues:**
```python
# Increase timeout
config = {'timeout': 10}
```

**SSL Certificate Errors:**
```python
# SSL Scanner ignores certificate verification by default
# This is intentional for reconnaissance purposes
```

## 📚 Examples

See `examples/camera_basic_example.py` for complete working examples.

## 🤝 Contributing

When adding new cameras:

1. Extend `BaseCamera` class
2. Choose appropriate `CameraMode`
3. Implement the `scan()` method
4. Record discoveries with `record_discovery()`
5. Add documentation and examples
6. Update this README

## 📄 License

Part of the Nethical Recon project.

---

**Next Wave:** Fala 3 - Forest (Infrastructure Mapping) 🌳
