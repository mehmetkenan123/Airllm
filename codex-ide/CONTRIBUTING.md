# Contributing to Codex IDE

Thank you for your interest in contributing to Codex IDE! This document provides guidelines and instructions for contributing.

## Code of Conduct

Please be respectful and constructive in your interactions. We welcome contributors of all backgrounds.

## Getting Started

### 1. Fork and Clone

```bash
git clone https://github.com/YOUR_USERNAME/codex-ide.git
cd codex-ide
```

### 2. Install Dependencies

```bash
pnpm install
```

### 3. Set Up Development Environment

```bash
# Install git hooks
pnpm prepare

# Verify setup
pnpm lint
pnpm typecheck
```

## Development Workflow

### Making Changes

1. Create a branch: `git checkout -b feature/your-feature`
2. Make changes
3. Run tests: `pnpm test`
4. Run type checking: `pnpm typecheck`
5. Format code: `pnpm format`
6. Commit with conventional commits: `git commit -m "feat: add new feature"`

### Commit Convention

We use [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `style:` Code style changes (formatting)
- `refactor:` Code refactoring
- `test:` Test additions/changes
- `chore:` Build/config changes

Example:
```
feat(ai-core): add streaming support for AirLLM backend

- Implement StreamingHandler class
- Add server-sent events support
- Update AI chat panel to handle streams

Closes #123
```

## Testing

### Unit Tests

```bash
pnpm test --filter packages/ai-core
```

### E2E Tests

```bash
pnpm test --filter tests/e2e
```

### Performance Benchmarks

```bash
pnpm test --filter tests/performance
```

## Pull Request Process

1. Ensure all tests pass
2. Update documentation if needed
3. Add tests for new features
4. Request review from maintainers
5. Address review feedback

## Architecture Guidelines

### Package Structure

Each package should:
- Have a clear single responsibility
- Export a well-defined API
- Include comprehensive types
- Have unit tests

### Code Style

- Use TypeScript strict mode
- Follow existing code patterns
- Add JSDoc comments for public APIs
- Keep functions small and focused

### Performance Considerations

- Minimize memory allocations
- Use workers for heavy computations
- Implement proper caching
- Lazy load when possible

## Questions?

Open an issue or join our discussions!
