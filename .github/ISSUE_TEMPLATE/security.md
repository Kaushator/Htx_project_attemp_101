---
name: 🔒 Security Issue
about: Report a security vulnerability (Please see Security Policy first)
title: '[SECURITY] '
labels: ['security', 'needs-triage']
assignees: ''
---

## ⚠️ SECURITY NOTICE ⚠️

**Before submitting a security issue publicly, please review our [Security Policy](SECURITY.md).**

For critical security vulnerabilities, please:
1. **DO NOT** create a public issue
2. Follow our responsible disclosure process
3. Contact the maintainers privately

## 🔒 Security Issue Type

**What type of security issue is this?**
- [ ] **Vulnerability**: Exploitable security flaw
- [ ] **Security Enhancement**: Suggestion to improve security
- [ ] **Configuration Issue**: Insecure default configuration
- [ ] **Dependency Issue**: Vulnerable dependency
- [ ] **Information Disclosure**: Unintended information exposure
- [ ] **Authentication/Authorization**: Access control issues
- [ ] **Input Validation**: Injection or validation bypass
- [ ] **Cryptographic Issue**: Weak encryption or key management

## 📊 Severity Assessment

**Please rate the severity of this issue:**

### CVSS Score (if known)
- **CVSS Score**: [e.g., 7.5]
- **CVSS Vector**: [e.g., CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N]

### Impact Level
- [ ] **Critical**: Complete system compromise, data breach
- [ ] **High**: Privilege escalation, significant data exposure
- [ ] **Medium**: Limited data exposure, DoS potential
- [ ] **Low**: Information disclosure, minor security improvement
- [ ] **Informational**: Security best practice suggestion

## 🎯 Affected Components

**Which parts of the system are affected?**
- [ ] **Backend API**: FastAPI endpoints
- [ ] **Authentication**: Login/token management
- [ ] **Database**: Data storage and queries
- [ ] **Frontend**: React application
- [ ] **Docker Configuration**: Container security
- [ ] **Dependencies**: Third-party libraries
- [ ] **Configuration**: Environment variables, settings
- [ ] **File Upload**: File processing functionality
- [ ] **External APIs**: HTX/3Commas integrations

## 🔍 Issue Description

**Provide a clear description of the security issue:**

### Summary
**Brief description of the vulnerability or security concern:**

### Technical Details
**Detailed technical description (remove if reporting privately):**
```
Provide technical details, but be mindful of public disclosure
```

### Attack Vector
**How could this be exploited?**
- **Attack Complexity**: [Low/Medium/High]
- **Required Privileges**: [None/Low/High]
- **User Interaction**: [Required/None]
- **Scope**: [Local/Remote]

## 🔄 Steps to Reproduce

**If this is a vulnerability, provide reproduction steps:**

⚠️ **Note**: Only include if this is not a critical vulnerability requiring private disclosure.

1. Step 1
2. Step 2
3. Step 3
4. Observe security issue

## 💥 Impact Assessment

**What is the potential impact of this issue?**

### Confidentiality
- [ ] No impact
- [ ] Limited information disclosure
- [ ] Significant information disclosure
- [ ] Complete information disclosure

### Integrity
- [ ] No impact
- [ ] Limited data modification
- [ ] Significant data modification
- [ ] Complete data compromise

### Availability
- [ ] No impact
- [ ] Limited service disruption
- [ ] Significant service disruption
- [ ] Complete service unavailability

### Business Impact
**Describe the potential business impact:**
- Data breach potential
- Compliance violations
- User trust issues
- Service availability

## 🛡️ Mitigation Recommendations

**Suggested fixes or mitigations:**

### Immediate Actions
- [ ] Disable affected feature
- [ ] Update configuration
- [ ] Apply temporary workaround
- [ ] Increase monitoring

### Long-term Fixes
- [ ] Code changes required
- [ ] Dependency updates
- [ ] Configuration changes
- [ ] Security controls implementation

### Recommended Solutions
**Describe your recommended fix:**
```
Provide implementation suggestions (if appropriate for public disclosure)
```

## 📋 Environment Information

**Environment where this issue was discovered:**
- **Version**: [e.g., latest from copilot-refactor branch]
- **Environment**: [e.g., development, staging, production]
- **Platform**: [e.g., Docker, local development]
- **Browser** (if frontend): [e.g., Chrome 118, Firefox 119]

## 🔗 References

**Related security information:**
- [ ] CVE ID: [if applicable]
- [ ] Related security advisories
- [ ] OWASP references
- [ ] Security research papers
- [ ] Similar vulnerabilities in other projects

### Links
- [Link to relevant security documentation]
- [Link to related CVEs or advisories]
- [Link to security best practices]

## 🕒 Timeline

**For vulnerability reports:**
- **Discovery Date**: [When was this discovered?]
- **Verification Date**: [When was it verified?]
- **First Reported**: [When was it first reported?]

## 👤 Disclosure Information

**Researcher/Reporter Information (optional):**
- **Name**: [Your name or organization]
- **Contact**: [Preferred contact method]
- **Credit Preference**: [How you'd like to be credited]

## ✅ Checklist

**Before submitting this security issue:**

- [ ] I have reviewed the [Security Policy](SECURITY.md)
- [ ] I have determined this is appropriate for public disclosure
- [ ] I have removed sensitive technical details that could aid attackers
- [ ] I have provided sufficient information for reproduction and fixing
- [ ] I have assessed the impact and severity appropriately
- [ ] I have followed responsible disclosure practices
- [ ] I understand that security issues require special handling

---

**Note**: If this is a critical security vulnerability, please consider private disclosure through our security contact channels instead of creating a public issue.