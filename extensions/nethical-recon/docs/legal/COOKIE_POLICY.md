# Cookie Policy

**Effective Date**: January 2026
**Last Updated**: January 2026
**Version**: 6.0

## Introduction

This Cookie Policy explains how Nethical Recon uses cookies and similar technologies.

## Important Notice

**Nethical Recon is primarily a command-line and API-based tool that runs on your infrastructure.**

### Current Usage

- **Core Software**: Does NOT use cookies (CLI, API, backend services)
- **Web UI** (if deployed): May use cookies for session management

### This Policy Applies To

- The Nethical Recon web interface (if you deploy it)
- Future web-based components
- Project website (if established)

**If you do not deploy the web UI, this policy does not apply to your usage.**

## What Are Cookies?

Cookies are small text files stored on your device by websites you visit. They are widely used to make websites work efficiently and provide information to site owners.

### Types of Cookies

**By Lifespan:**

- **Session Cookies**: Temporary, deleted when you close your browser
- **Persistent Cookies**: Remain until expiration date or manual deletion

**By Purpose:**

- **Strictly Necessary**: Required for the site to function
- **Functional**: Remember your preferences
- **Analytics**: Understand how visitors use the site
- **Advertising**: Deliver relevant ads (NOT USED by Nethical Recon)

## Cookies Used by Nethical Recon Web UI

If you deploy the Nethical Recon web interface, the following cookies may be used:

### 1. Strictly Necessary Cookies

These cookies are essential for the web interface to function and cannot be disabled.

| Cookie Name | Purpose | Duration | Type |
|------------|---------|----------|------|
| `session_id` | User authentication session | Session | HTTP-only, Secure |
| `csrf_token` | Cross-Site Request Forgery protection | Session | HTTP-only, Secure |
| `auth_token` | API authentication token | Configurable | HTTP-only, Secure |

**Legal Basis**: Legitimate interest (essential functionality)
**Can be disabled**: No (site won't work without them)

### 2. Functional Cookies

These cookies enable enhanced functionality and personalization.

| Cookie Name | Purpose | Duration | Type |
|------------|---------|----------|------|
| `ui_preferences` | UI theme, language, layout preferences | 1 year | Standard |
| `recent_scans` | Quick access to recent scans | 30 days | Standard |
| `sidebar_state` | Remember sidebar collapsed/expanded | 1 year | Standard |

**Legal Basis**: Consent or legitimate interest
**Can be disabled**: Yes (through settings)

### 3. Analytics Cookies (Optional)

**Nethical Recon does NOT include analytics by default.**

If you configure analytics integrations:

| Purpose | Provider | Duration | Type |
|---------|----------|----------|------|
| Usage analytics | Your choice | Varies | Third-party |

**Legal Basis**: Consent (opt-in)
**Can be disabled**: Yes (don't configure analytics)

### 4. Advertising Cookies

**Nethical Recon does NOT use advertising cookies.**

We do not:
- ❌ Show advertisements
- ❌ Track users for advertising
- ❌ Share data with ad networks

## Cookie Settings and Consent

### Web UI Cookie Settings

If the web UI is deployed, users can manage cookies through:

1. **Settings Panel**: UI Preferences → Privacy → Cookie Settings
2. **Browser Settings**: Most browsers allow cookie management
3. **Configuration File**: Admin can disable optional cookies

### Cookie Consent Banner

The web UI may display a cookie consent banner on first visit (EU requirement).

**Options:**

- ✅ **Accept All**: Allow all cookies
- ⚙️ **Customize**: Choose which cookie categories to allow
- ❌ **Reject Optional**: Only strictly necessary cookies

### Granular Control

Users can control:

- Functional cookies (ON/OFF)
- Analytics cookies (if configured) (ON/OFF)

**Strictly necessary cookies** cannot be disabled (site won't function).

## Third-Party Cookies

### Default Configuration

Nethical Recon does NOT set third-party cookies by default.

### Optional Integrations

If you configure integrations, third-party cookies may be set:

**Potential Third-Party Services:**

- **Single Sign-On (SSO)**: OAuth providers (Google, Okta, etc.)
- **Analytics**: If you configure Google Analytics, Matomo, etc.
- **Chat/Support**: If you embed support widgets

**Your Responsibility:**

- Review third-party privacy policies
- Obtain necessary consent
- Update your privacy policy accordingly
- Use cookie consent management if required

## How to Control Cookies

### Browser Settings

All major browsers allow cookie management:

#### Google Chrome

1. Settings → Privacy and security → Cookies and other site data
2. Choose: Allow all / Block third-party / Block all

#### Mozilla Firefox

1. Settings → Privacy & Security → Cookies and Site Data
2. Choose blocking level and manage exceptions

#### Safari

1. Preferences → Privacy → Cookies and website data
2. Choose blocking level

#### Microsoft Edge

1. Settings → Privacy, search, and services → Cookies and site data
2. Choose blocking level

### Clear Cookies

To delete existing cookies:

- **Chrome**: Settings → Privacy and security → Clear browsing data
- **Firefox**: Settings → Privacy & Security → Clear Data
- **Safari**: Preferences → Privacy → Manage Website Data → Remove All
- **Edge**: Settings → Privacy → Clear browsing data

## Local Storage and Other Technologies

Besides cookies, web applications may use:

### Local Storage

**Purpose**: Store larger amounts of data locally
**Usage in Nethical Recon**:
- Cached scan results
- UI preferences
- Temporary data

**Location**: Browser's local storage
**Persistence**: Until manually cleared

### Session Storage

**Purpose**: Temporary storage for current session
**Usage in Nethical Recon**:
- Form data during multi-step scans
- Temporary UI state

**Location**: Browser's session storage
**Persistence**: Until tab/window is closed

### IndexedDB

**Purpose**: Client-side database for structured data
**Usage in Nethical Recon**:
- Offline capability
- Large dataset caching

**Location**: Browser's IndexedDB
**Persistence**: Until manually cleared

### Web Storage Management

To clear web storage:

1. **Chrome**: DevTools → Application → Storage → Clear site data
2. **Firefox**: DevTools → Storage → Right-click → Delete All
3. **Safari**: Preferences → Privacy → Manage Website Data
4. **Edge**: DevTools → Application → Storage → Clear

## Do Not Track (DNT)

### DNT Signal Support

The Nethical Recon web UI respects the Do Not Track (DNT) browser setting.

**When DNT is enabled:**

- ✅ Analytics cookies are disabled (if configured)
- ✅ Optional tracking is disabled
- ✅ Only strictly necessary cookies are set

**To enable DNT:**

- **Chrome**: Settings → Privacy and security → Send a "Do not track" request
- **Firefox**: Settings → Privacy & Security → Send websites a "Do Not Track" signal
- **Safari**: Preferences → Privacy → Website tracking: Prevent cross-site tracking
- **Edge**: Settings → Privacy → Send "Do Not Track" requests

## GDPR Compliance (EU Users)

### Your Rights

Under GDPR, you have the right to:

- ✅ Know what cookies are used
- ✅ Give or withdraw consent
- ✅ Access your data
- ✅ Delete your data

### Cookie Consent

For EU users, the web UI implements:

- **Opt-in consent**: For non-essential cookies
- **Granular choices**: Per cookie category
- **Easy withdrawal**: Change preferences anytime
- **Cookie banner**: Clear information and choices

### Legitimate Interest

We rely on legitimate interest for:

- Strictly necessary cookies (essential functionality)
- Security cookies (fraud prevention, security)

### Data Protection Officer

If your organization has a DPO, include contact information:

📧 **DPO Email**: dpo@your-organization.example

## CCPA Compliance (California Users)

### Your Rights

Under CCPA, California residents have the right to:

- ✅ Know what information is collected
- ✅ Request deletion
- ✅ Opt-out of "sale" (not applicable - we don't sell data)

### "Do Not Sell" Notice

**Nethical Recon does NOT sell your data.**

Cookies are used solely for functionality and analytics (if configured).

## Security

### Cookie Security

Nethical Recon implements cookie security best practices:

🔒 **HttpOnly Flag**: Prevents JavaScript access (where appropriate)
🔒 **Secure Flag**: Only transmitted over HTTPS
🔒 **SameSite Attribute**: Protects against CSRF
🔒 **Short Expiration**: Sessions expire after inactivity
🔒 **Encryption**: Sensitive cookie data is encrypted

### Recommendations

For administrators deploying the web UI:

- ✅ Use HTTPS/TLS for all connections
- ✅ Configure secure cookie settings
- ✅ Regular security updates
- ✅ Monitor for suspicious activity
- ✅ Implement session timeout

## Children's Privacy

Nethical Recon is not intended for children under 13 (or 16 in EU).

We do not knowingly:

- ❌ Set cookies on children's devices
- ❌ Collect data from children
- ❌ Target children with content

If you operate the web UI, implement age restrictions if necessary.

## Updates to This Policy

This Cookie Policy may be updated to reflect:

- Changes in technology
- Legal requirements
- New features

**Notification of Updates:**

- "Last Updated" date modified
- Significant changes announced
- Users re-prompted for consent (if required)

**Your Action**: Review this policy periodically.

## Contact Information

### Cookie Policy Questions

For questions about this Cookie Policy:

📧 **Email**: privacy@nethical-recon.example

### Data Protection Officer

📧 **DPO**: dpo@your-organization.example (if applicable)

### Cookie Consent Management

To manage cookie preferences:

- **Web UI**: Settings → Privacy → Cookie Settings
- **Browser**: Use browser cookie controls
- **Opt-out**: Disable optional cookies

## Technical Implementation Notes

### For Administrators

When deploying the web UI:

```python
# Example: Configure cookie settings
COOKIE_SETTINGS = {
    "SESSION_COOKIE_SECURE": True,  # HTTPS only
    "SESSION_COOKIE_HTTPONLY": True,  # No JavaScript access
    "SESSION_COOKIE_SAMESITE": "Lax",  # CSRF protection
    "SESSION_COOKIE_NAME": "nethical_session",
    "PERMANENT_SESSION_LIFETIME": 3600,  # 1 hour
}
```

### Cookie Consent Implementation

```javascript
// Example: Check cookie consent
if (hasConsent('analytics')) {
    // Load analytics
    loadAnalytics();
}

// Honor DNT signal
if (navigator.doNotTrack === "1") {
    disableOptionalCookies();
}
```

## Additional Resources

### Standards and Guidelines

- **ePrivacy Directive**: https://ec.europa.eu/digital-single-market/en/eprivacy-directive
- **GDPR**: https://gdpr.eu/cookies/
- **ICO Cookie Guidance**: https://ico.org.uk/for-organisations/guide-to-pecr/cookies-and-similar-technologies/

### Tools

- **Cookie Audit Tools**: Browser DevTools, CookieMetrix
- **Consent Management Platforms**: Various CMPs available
- **Cookie Policy Generators**: For creating custom policies

## Disclaimer

This Cookie Policy is provided for informational purposes and does not constitute legal advice.

**Recommendations:**

- Consult legal counsel for your jurisdiction
- Customize this policy for your deployment
- Conduct cookie audit before going live
- Maintain documentation of consent

## Summary

### Key Points

✅ **Core software**: No cookies (CLI, API)
✅ **Web UI**: Minimal cookies for functionality
✅ **No tracking**: We don't track users or sell data
✅ **Control**: You control what cookies are set
✅ **Security**: Cookies are secured with best practices
✅ **Consent**: Required for non-essential cookies (EU)

### Your Choices

- ✅ Deploy without web UI (no cookies)
- ✅ Use only essential cookies
- ✅ Configure cookie consent management
- ✅ Respect user preferences
- ✅ Clear cookies anytime

---

**Last Updated**: January 2026
**Version**: 6.0
**Applies to**: Nethical Recon Web UI

---

**Questions?** Contact privacy@nethical-recon.example
