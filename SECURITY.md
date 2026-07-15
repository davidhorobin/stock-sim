# Security Policy
 
## Supported Versions
 
This project is maintained on the `main` branch only. There are no released
versions with independent security support — please always use the latest
commit on `main`.
 
| Version | Supported          |
| ------- | ------------------ |
| main    | :white_check_mark: |
| other   | :x:                |
 
## Reporting a Vulnerability
 
This is a personal/educational project (no real money or real user funds are
involved), but reports are still welcome.
 
If you discover a security vulnerability, do not open a public
GitHub issue. Instead:
 
1. Open a [private security advisory](https://github.com/davidhorobin/stock-sim/security/advisories/new)
   on GitHub, or
2. Email the me directly (see GitHub profile for contact details).
Please include:
 
- A description of the vulnerability and its potential impact
- Steps to reproduce it
- Any relevant logs, screenshots, or proof-of-concept code
If the issue is confirmed, a fix will be prioritized and you'll be credited (unless you'd
prefer to remain anonymous) once it's resolved.
 
## Scope
 
Known areas of relevance for this project:
 
- Authentication (registration/login, password hashing, session handling)
- SQL query construction (parameterized vs. unparameterized queries)
- Handling of the `SECRET_KEY` and instance configuration
- Third-party data fetching (yfinance, market news RSS feed)
Since this app stores only virtual cash and does not process real payments,
issues here are lower severity than in a production financial application —
but authentication, session, and injection-related bugs are still taken
seriously.
