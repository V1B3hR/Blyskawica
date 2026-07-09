# Export Compliance

**Effective Date**: January 2026
**Version**: 6.0

## Overview

This document addresses export control compliance for Nethical Recon, an open-source security reconnaissance and penetration testing tool.

⚠️ **IMPORTANT**: This document provides general guidance and is not legal advice. Consult with legal counsel and export compliance experts for your specific situation.

## Executive Summary

**Nethical Recon may be subject to export control regulations** in various jurisdictions, including:

- 🇺🇸 United States Export Administration Regulations (EAR)
- 🇪🇺 European Union Dual-Use Regulations
- 🇬🇧 United Kingdom Export Control Act
- 🌍 Other national export control laws

**Key Points:**

- ✅ Software is generally available on GitHub (publicly available)
- ⚠️ May contain encryption (subject to controls)
- ⚠️ Security/penetration testing tool (potential dual-use)
- ✅ Open-source license (may qualify for exemptions)

## United States Export Controls

### Export Administration Regulations (EAR)

Administered by the U.S. Bureau of Industry and Security (BIS).

#### Potential Classifications

**Encryption Functionality (ECCN 5D002):**

- Nethical Recon may use encryption libraries (e.g., TLS/SSL, SSH)
- Encryption items are controlled under ECCN 5D002

**Security Testing Tools (ECCN 5A004):**

- Penetration testing and security tools may fall under ECCN 5A004.d
- "Network penetration" and "security vulnerability" testing tools

**Software with Encryption (ECCN 5D992):**

- Mass market encryption software
- Publicly available encryption source code

#### License Exceptions

**ENC (Encryption):**

- May apply to encryption components
- Requirements: Self-classification, annual self-classification reports to BIS
- Publicly available source code may qualify

**TSU (Technology and Software Unrestricted):**

- Publicly available software may qualify
- Must be available to the general public
- No export controls applied to access

**Mass Market Exception:**

- May apply if meets mass market criteria
- Generally available to the public

### OFAC Sanctions

The Office of Foreign Assets Control (OFAC) prohibits exports to:

**Embargoed Countries** (as of 2026):
- 🚫 Cuba
- 🚫 Iran
- 🚫 North Korea
- 🚫 Syria
- 🚫 Crimea region of Ukraine
- 🚫 Other sanctioned regions (check current list)

**Restricted Parties:**
- 🚫 Specially Designated Nationals (SDN) List
- 🚫 Denied Persons List
- 🚫 Entity List
- 🚫 Unverified List

**Compliance:** Check OFAC lists before providing software or services.

### Open Source Exemptions

**Potential Applicability:**

Under EAR §734.7 and §742.15(b), publicly available encryption source code may be exempt from license requirements if:

1. ✅ Available to the public (e.g., GitHub)
2. ✅ No export controls applied to access
3. ✅ Notification to BIS (one-time, for certain encryption)

**Notification Requirement:**

- May need to notify BIS of publicly available encryption source code
- Email: crypt@bis.doc.gov with specific information
- Provide URL, point of contact, and encryption details

### Deemed Export Rules

**Warning:** Sharing controlled technology with foreign nationals **in the United States** may constitute a "deemed export."

**Compliance:**
- Review contributor nationality (for controlled items)
- May need licenses for certain nationalities
- Exemptions may apply for fundamental research

## European Union Export Controls

### EU Dual-Use Regulation (EU) 2021/821

Applies to dual-use items (civilian and military use).

#### Potential Classifications

**Category 5 Part 2 - Information Security:**

- Encryption software and systems
- Network penetration tools
- Security vulnerability testing tools

**Annex I Controls:**

- May apply to security testing software

#### Export Authorization

**Within EU:** Generally no license required
**Outside EU:** May require export authorization depending on:
- Destination country
- End-user
- End-use

#### Open Source Exception

**Article 3(2)(a)**: Software in the public domain is generally not subject to controls.

**Criteria:**
- ✅ Freely available without restrictions
- ✅ Not subject to intellectual property restrictions (or under open license)

### Member State Regulations

Export controls are enforced by **individual EU member states**. Check national regulations for:

- 🇩🇪 Germany: Federal Office for Economic Affairs and Export Control (BAFA)
- 🇫🇷 France: Service des Biens à Double Usage (SBDU)
- 🇳🇱 Netherlands: Netherlands Enterprise Agency (RVO)
- Other member states: National export control authorities

## United Kingdom Export Controls

### Export Control Act 2002 and Export Control Order 2008

Administered by the Export Control Joint Unit (ECJU).

#### Potential Classifications

**Category 5 Part 2:**
- Information security equipment and software
- Security testing tools

#### Open Source Software

Publicly available software may be exempt from licensing requirements under:

- **Note 4 to Category 5 Part 2**: Software that is generally available to the public

**Criteria:**
- ✅ Available without restriction
- ✅ Not tailored for specific military or government use

### Embargoes and Sanctions

UK maintains its own sanctions list (separate from EU post-Brexit):

- 🚫 Check UK Sanctions List
- 🚫 Follow OFAC SDN List (for U.S. nexus transactions)

## Other Jurisdictions

### Canada

**Export and Import Permits Act:**
- Administered by Global Affairs Canada
- Dual-use export controls similar to U.S. and EU

### Australia

**Defence and Strategic Goods List:**
- Administered by Department of Defence
- Controls on security testing and encryption tools

### Other Countries

Consult local export control authorities in your jurisdiction.

## GitHub and Open Source Distribution

### GitHub as Distribution Platform

**Considerations:**

- ✅ GitHub provides global access (public repositories)
- ⚠️ Users may be in embargoed countries
- ✅ No export controls applied to repository access

**GitHub's Policies:**

- GitHub blocks access from sanctioned countries (trade controls)
- See: https://docs.github.com/en/site-policy/other-site-policies/github-and-trade-controls

### Open Source License (Apache 2.0)

**License Provisions:**

- Permissive license allowing redistribution
- No export control provisions in license itself
- Users are responsible for export compliance

## Compliance Recommendations

### For Project Maintainers

1. **Determine Classification:**
   - Conduct self-classification (or engage consultant)
   - Identify applicable ECCNs or classification codes
   - Document classification rationale

2. **Notification (if required):**
   - File one-time notification with BIS (if encryption)
   - Maintain records of notification

3. **License and Documentation:**
   - Include export compliance notice in README
   - Inform users of their responsibilities
   - Provide guidance on restrictions

4. **Screen Contributors:**
   - Be aware of deemed export rules
   - May need screening for certain contributions
   - Exemptions may apply (fundamental research, public domain)

5. **Monitor Sanctions:**
   - Regularly check OFAC and other sanctions lists
   - Update documentation when regulations change

### For Users and Distributors

1. **Understand Restrictions:**
   - Review applicable export controls in your jurisdiction
   - Determine if license required for your use/distribution

2. **End-User Restrictions:**
   - Do not provide to embargoed countries or sanctioned parties
   - Ensure end-use is lawful and authorized

3. **Obtain Licenses (if required):**
   - Apply for export licenses if necessary
   - Consult with export compliance professionals

4. **Document Compliance:**
   - Maintain records of export compliance efforts
   - Document self-classification and license exceptions

## Export Compliance Statement

**Nethical Recon is distributed as open-source software under the Apache 2.0 license.**

### User Responsibilities

**BY DOWNLOADING, INSTALLING, OR USING NETHICAL RECON, YOU AGREE:**

1. ✅ You are not located in an embargoed country
2. ✅ You are not on any government prohibited or restricted party list
3. ✅ You will comply with all applicable export control laws and regulations
4. ✅ You will not export or re-export the Software in violation of applicable laws
5. ✅ You will obtain necessary export licenses if required
6. ✅ You will not use the Software for prohibited end-uses (e.g., WMD development)

### Restricted Countries and Parties

**DO NOT download or use** Nethical Recon if:

- ❌ You are located in an embargoed country (Cuba, Iran, North Korea, Syria, etc.)
- ❌ You are on the OFAC SDN List, Denied Persons List, Entity List, or similar
- ❌ You intend to use the Software for prohibited purposes
- ❌ You intend to provide the Software to restricted parties

### Violations

**Violations of export control laws can result in:**

- Criminal prosecution
- Civil penalties and fines
- Imprisonment
- Loss of export privileges
- Damage to reputation

## Technical Measures

### Encryption Usage

Nethical Recon may use encryption for:

- TLS/SSL connections
- SSH tunneling
- Encrypted data storage
- API authentication (JWT, etc.)

**Encryption Libraries Used:**
- OpenSSL, cryptography (Python), or similar
- Generally publicly available encryption libraries

### Encryption Strength

**Symmetric:** AES-128, AES-256
**Asymmetric:** RSA-2048, RSA-4096, ECDSA
**Hashing:** SHA-256, SHA-512

## Deemed Export Considerations

### Contributor Access to Controlled Technology

If Nethical Recon contains controlled technology (e.g., advanced encryption algorithms), sharing with foreign nationals may be a deemed export.

**Exemptions May Apply:**

- **Educational Information**: Generally available academic knowledge
- **Publicly Available**: Information in the public domain
- **Fundamental Research**: Basic and applied research results

### Open Source Collaboration

**GitHub Collaboration:**

- Contributors from various countries
- Public code review and discussion
- May qualify for public domain exception

**Best Practices:**

- Document that project is publicly available
- No restrictions on access (except sanctioned countries via GitHub)
- Fundamental research exception may apply

## Updates and Monitoring

### Regulatory Changes

Export control regulations change frequently. Monitor:

- BIS (U.S.): https://www.bis.doc.gov/
- EU Commission: https://ec.europa.eu/trade/import-and-export-rules/export-from-eu/dual-use-controls/
- UK ECJU: https://www.gov.uk/government/organisations/export-control-joint-unit

### Sanctions Updates

Check sanctions lists regularly:

- OFAC (U.S.): https://sanctionssearch.ofac.treas.gov/
- EU Sanctions: https://www.sanctionsmap.eu/
- UN Sanctions: https://www.un.org/securitycouncil/sanctions/information

## Resources

### U.S. Resources

- **BIS**: https://www.bis.doc.gov/
- **ECCN Guide**: https://www.bis.doc.gov/index.php/licensing/commerce-control-list-classification
- **Encryption Registration**: crypt@bis.doc.gov
- **OFAC**: https://home.treasury.gov/policy-issues/office-of-foreign-assets-control-sanctions-programs-and-information

### EU Resources

- **Dual-Use Regulation**: https://ec.europa.eu/trade/import-and-export-rules/export-from-eu/dual-use-controls/
- **Member State Authorities**: Contact national export control office

### UK Resources

- **ECJU**: https://www.gov.uk/government/organisations/export-control-joint-unit
- **Guidance**: https://www.gov.uk/guidance/beginners-guide-to-export-controls

### Legal Assistance

For complex situations, consult:

- Export control attorneys
- Compliance consultants
- Trade compliance firms

## Disclaimer

**THIS DOCUMENT IS NOT LEGAL ADVICE.**

Export control laws are complex and subject to interpretation. The information provided here is for general guidance only.

**You should:**

- Consult with qualified legal counsel
- Engage export compliance professionals
- Conduct your own compliance assessment
- Stay informed of regulatory changes

**The Nethical Recon project:**

- Makes no warranties regarding export classification
- Is not responsible for users' export compliance
- Provides this information as-is for educational purposes

## Contact

### Export Compliance Questions

For questions about export compliance:

📧 **Email**: legal@nethical-recon.example

**Note:** We are not export compliance experts. This information is general guidance only.

### Report Violations

If you become aware of export control violations:

- U.S.: Report to BIS or OFAC
- EU: Report to national authority
- UK: Report to ECJU

## Acknowledgment

By using Nethical Recon, you acknowledge that:

✅ You have read this export compliance document
✅ You understand your export compliance responsibilities
✅ You will comply with all applicable export control laws
✅ You will not violate sanctions or embargoes
✅ You accept full responsibility for your compliance

---

**Last Updated**: January 2026
**Version**: 6.0

---

**THINK BEFORE YOU EXPORT. UNDERSTAND THE RULES. COMPLY WITH THE LAW.**
