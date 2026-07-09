# Security Policy

## Supported Versions

We actively support the following versions of Nethical Recon with security updates:

| Version | Supported          |
|---------|-------------------|
| 6.x.x   | ✅ Yes (Current)  |
| 5.x.x   | ✅ Yes            |
| 4.x.x   | ⚠️ Security only  |
| < 4.0   | ❌ No             |

## Reporting Security Vulnerabilities

We take security vulnerabilities seriously and appreciate your efforts to responsibly disclose your findings.

### Contact Methods

Please report security vulnerabilities through one of the following channels:

- **🐛 GitHub Security Advisories** (preferred method)
  - Navigate to the [Security tab](https://github.com/V1B3hR/nethical-recon/security/advisories)
  - Click "Report a vulnerability"

- **📧 Email**: security@nethical-recon.example
  - For encrypted communication, use our PGP key (see below)

- **🔐 PGP Key**:
  ```
  [PGP PUBLIC KEY TO BE ADDED]
  Key ID: [TO BE GENERATED]
  Fingerprint: [TO BE GENERATED]
  ```

**🚫 DO NOT** report security vulnerabilities through public GitHub issues, discussions, or any other public forum.

### Response Timeline Commitments

We are committed to addressing security vulnerabilities promptly:

- **24 hours**: Initial acknowledgment of your report
- **7 days**: Severity assessment and triage completion
- **30 days**: Preliminary fix or mitigation guidance provided
- **90 days**: Public disclosure or coordinated disclosure with your agreement

We will keep you informed throughout the process and work with you to understand and address the issue.

## Scope

### In Scope

The following vulnerabilities are within scope for security reports:

✅ **API Security Issues**
- Authentication vulnerabilities
- Authorization bypasses
- SQL/NoSQL/Command injection
- API abuse or rate limiting bypasses
- Insecure deserialization

✅ **Infrastructure Security**
- Worker queue security issues
- Secrets management flaws
- Database security issues
- Container escape or privilege escalation

✅ **Application Security**
- Plugin marketplace security vulnerabilities
- Privilege escalation in the application
- Data leakage or exposure
- Authentication bypass
- Session management issues

✅ **Web Security** (if applicable)
- Server-Side Request Forgery (SSRF)
- Cross-Site Scripting (XSS)
- Cross-Site Request Forgery (CSRF)
- Insecure direct object references

✅ **Cryptography**
- Weak encryption algorithms
- Improper certificate validation
- Insecure key storage

### Out of Scope

The following are generally not considered security vulnerabilities:

❌ Denial of Service (DoS) attacks
- Rate limiting is intentionally configurable
- Resource exhaustion through normal usage

❌ Social Engineering
- Phishing attacks against users
- Social manipulation tactics

❌ Physical Security
- Physical access to servers or infrastructure

❌ Third-Party Dependencies
- Vulnerabilities in third-party libraries (please report to upstream maintainers)
- We will address these during regular dependency updates

❌ Requires Physical Access
- Issues that require local system access

❌ Theoretical Vulnerabilities
- Vulnerabilities without a working Proof of Concept (PoC)
- Issues that cannot be exploited in practice

❌ Issues Already Known
- Check existing security advisories first

## Safe Harbor Policy

We support good-faith security research and will not pursue legal action against researchers who:

✅ Make a good-faith effort to avoid privacy violations, data destruction, and service disruption
✅ Only interact with accounts you own or with explicit permission from the account holder
✅ Do not exploit a vulnerability beyond the minimum necessary to demonstrate it
✅ Give us reasonable time to fix the issue before public disclosure
✅ Do not access, modify, or delete data belonging to others
✅ Comply with all applicable laws and regulations

### Our Commitments

In return, we commit to:

✅ Respond to your report promptly and keep you informed of our progress
✅ Work with you to understand and validate the issue
✅ Credit you for the discovery (unless you prefer to remain anonymous)
✅ Not pursue legal action against researchers who comply with this policy
✅ Consider your report for our security researcher recognition program

## Recognition Program

We believe in recognizing security researchers who help us improve Nethical Recon's security.

### Hall of Fame

Security researchers who report valid vulnerabilities will be listed in our Security Hall of Fame (with your permission).

### Recognition Levels

- **🔴 Critical Severity**
  - Featured recognition in release notes
  - Prominent placement in Hall of Fame
  - Potential bug bounty (future program)

- **🟠 High Severity**
  - Public acknowledgment in security advisory
  - Hall of Fame listing

- **🟡 Medium Severity**
  - Credits in changelog
  - Hall of Fame listing

- **🟢 Low Severity**
  - Internal recognition
  - Optional Hall of Fame listing

### Anonymity

If you prefer to remain anonymous, we will respect your wishes and will not publicly attribute the discovery to you.

## Security Best Practices for Users

As a security tool, Nethical Recon users should follow these best practices:

1. **Keep Updated**: Always use the latest version with security patches
2. **Secure Configuration**: Follow security hardening guidelines in documentation
3. **Access Control**: Implement proper authentication and authorization
4. **Secrets Management**: Use environment variables or secret managers, never hardcode credentials
5. **Network Security**: Deploy behind firewalls and use TLS/SSL for all connections
6. **Audit Logging**: Enable comprehensive logging for security monitoring
7. **Principle of Least Privilege**: Run with minimal necessary permissions

## Security Updates

Security updates are released as soon as possible after a vulnerability is confirmed and fixed.

- **Critical/High**: Emergency patch release
- **Medium/Low**: Included in next scheduled release

Subscribe to our [GitHub Security Advisories](https://github.com/V1B3hR/nethical-recon/security/advisories) to receive notifications.

## Questions?

If you have questions about this security policy, please contact security@nethical-recon.example.

---

**Last Updated**: January 2026
**Version**: 6.0
