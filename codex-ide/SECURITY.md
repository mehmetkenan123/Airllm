# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |

## Reporting a Vulnerability

We take the security of Codex IDE seriously. If you believe you have found a security vulnerability, please report it to us as described below.

**Please do NOT report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to security@codex-ide.dev or create a draft security advisory on GitHub.

You should receive a response within 48 hours. If for some reason you do not, please follow up via email to ensure we received your original message.

After the initial reply to your report, we will send you a more detailed response indicating the next steps in handling your report. After the initial reply, we will keep you informed of the progress toward a fix and full announcement, and may ask for additional information or guidance.

## Security Best Practices

### For Users

1. **Model Sources**: Only download models from trusted sources (Hugging Face official repositories)
2. **Extensions**: Review extension permissions before installing
3. **Updates**: Keep Codex IDE updated to the latest version
4. **Sensitive Data**: Enable privacy filter in settings

### For Developers

1. **Dependencies**: Keep all dependencies updated
2. **Code Review**: All code changes require review
3. **Testing**: Security-focused testing in CI/CD
4. **Static Analysis**: CodeQL and similar tools enabled

## Known Limitations

1. **Local Models**: Model files are not encrypted at rest
2. **Extension Sandbox**: Extensions run with same privileges as main process (planned improvement)
3. **Network Requests**: Extensions can make network requests (user should review permissions)

## Security Features

- ✅ No telemetry by default
- ✅ Privacy filter for sensitive data
- ✅ Local-only AI inference (default)
- ✅ Open source codebase for auditing
- ✅ Sandboxed preload scripts
- ✅ Context isolation in Electron

## Bug Bounty Program

Currently, we do not have a formal bug bounty program. However, we greatly appreciate responsible disclosure and will acknowledge contributors who help improve our security.
