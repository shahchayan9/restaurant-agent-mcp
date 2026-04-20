# GitHub Actions CI/CD Setup

This document explains the automated testing and deployment setup for the MCP Restaurant Booking server.

## 🤖 Automated Workflows

### 1. **CI Pipeline** (`.github/workflows/ci.yml`)
Runs on every push and pull request to `main` and `develop` branches.

**What it does:**
- Tests on Node.js 18.x and 20.x
- Runs linting, type checking, and formatting checks
- Executes full test suite with coverage
- Performs security audit
- Validates build process

**Status checks:**
- ✅ All tests pass
- ✅ Code style is consistent  
- ✅ TypeScript compiles without errors
- ✅ No high/critical security vulnerabilities
- ✅ Build artifacts are created successfully

### 2. **PR Checks** (`.github/workflows/pr-checks.yml`)
Enhanced validation specifically for pull requests.

**What it does:**
- Validates PR title format (conventional commits)
- Runs performance tests and benchmarks
- Generates test coverage reports
- Adds automated comments with results
- Code quality analysis with SARIF upload

**PR Requirements:**
- PR title must follow format: `feat:`, `fix:`, `docs:`, etc.
- All performance tests must pass
- No performance regressions detected
- Test coverage maintained

### 3. **Performance Monitoring** (`.github/workflows/performance-monitoring.yml`)
Daily automated performance monitoring and regression detection.

**What it does:**
- Runs performance benchmarks daily at 2 AM UTC
- Tracks performance metrics over time
- Detects performance regressions automatically
- Monitors memory usage and potential leaks
- Stores benchmark results as artifacts

**Performance Thresholds:**
- Search time: < 2000ms
- Recommendation time: < 100ms
- Memory usage: < 50MB increase per 100 operations

## 🔧 Required Secrets

Add these secrets in your GitHub repository settings:

```bash
# GitHub Settings > Security > Secrets and variables > Actions

GOOGLE_MAPS_API_KEY_TEST=your_test_api_key_here
```

**Note:** Use a separate API key for testing with appropriate quotas and restrictions.

## 📋 Pull Request Template

When creating PRs, you'll see an automatic template with:
- Description guidelines
- Change type checkboxes
- Testing checklist
- Performance impact assessment
- Related issues linking

## 🚨 Issue Templates

Two issue templates are provided:

### Bug Report (`.github/ISSUE_TEMPLATE/bug_report.md`)
- Structured bug reporting
- Environment details
- Reproduction steps
- Performance impact assessment

### Feature Request (`.github/ISSUE_TEMPLATE/feature_request.md`)
- Feature description and motivation
- Implementation ideas
- Acceptance criteria
- Testing and documentation requirements

## 📊 Workflow Status Badges

Add these badges to your README.md:

```markdown
![CI Pipeline](https://github.com/yourusername/mcp-booking/workflows/CI%20Pipeline/badge.svg)
![PR Checks](https://github.com/yourusername/mcp-booking/workflows/PR%20Checks/badge.svg)
![Performance Monitoring](https://github.com/yourusername/mcp-booking/workflows/Performance%20Monitoring/badge.svg)
```

## 🎯 Performance Targets

The automated tests enforce these performance targets:

| Metric | Target | Enforced By |
|--------|--------|-------------|
| **Search Completion** | < 2 seconds | Performance tests |
| **API Calls per Search** | < 20 calls | Integration tests |
| **Memory Usage** | < 50MB/100 ops | Memory leak tests |
| **Concurrent Requests** | 5+ simultaneous | Concurrency tests |
| **Cache Hit Rate** | > 40% | Caching tests |

## 🔍 Local Testing

Before pushing, run these commands locally:

```bash
# Quality checks (same as CI)
npm run quality

# Full test suite
npm test

# Performance benchmarks
npm run benchmark

# Test coverage
npm run test:coverage
```

## 🐛 Troubleshooting

**Common CI Failures:**

1. **Test failures**: Check test output in Actions tab
2. **Linting errors**: Run `npm run lint:fix` locally
3. **Type errors**: Run `npm run type-check` locally
4. **Performance regression**: Check if changes impact search speed
5. **Security issues**: Review npm audit output

**Performance Monitoring Alerts:**

If daily performance monitoring fails:
1. Check if there are breaking changes in dependencies
2. Review recent commits for performance impact
3. Check Google Maps API quotas and limits
4. Verify test environment configuration

## 🚀 Deployment

The CI pipeline validates code but doesn't deploy automatically. For deployment:

1. All checks must pass
2. Create a release tag
3. Deploy using your preferred method (Docker, serverless, etc.)

The `dist/` folder contains the compiled JavaScript ready for production deployment.

## 📈 Monitoring in Production

Consider adding these monitoring tools:
- Performance monitoring (New Relic, Datadog)
- Error tracking (Sentry, Rollbar)
- API usage monitoring
- Cost tracking for Google Maps API

## 🔒 Security

The workflows include:
- Dependency vulnerability scanning
- Secret scanning prevention  
- Automated security updates via Dependabot
- Code quality analysis with GitHub security features

Never commit API keys or sensitive data - use GitHub Secrets instead.