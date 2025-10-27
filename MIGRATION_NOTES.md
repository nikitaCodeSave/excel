# Migration Notes - Package Updates October 2025

## ⚠️ Breaking Changes

This update includes several **major version updates** with breaking changes. Review carefully before deploying.

## Backend Updates (Python)

### Critical Updates

#### 1. **PydanticAI: 0.0.14 → 1.6.0** 🔴 BREAKING
- **Major version bump** from pre-release to stable v1
- API may have changed significantly
- **Action Required**: Review [PydanticAI changelog](https://ai.pydantic.dev/changelog/)
- Test all agent implementations after update

#### 2. **NumPy: 1.26.4 → 2.3.4** 🔴 BREAKING
- NumPy 2.0 introduced breaking changes
- **Compatibility**: Verified with pandas 2.3.0
- Some deprecated APIs removed
- **Action Required**: Test pandas operations, especially custom numpy code

#### 3. **FastAPI: 0.115.0 → 0.120.0** 🟡 MINOR BREAKING
- Added Python 3.14 support
- Pydantic v1 support deprecated (will be removed soon)
- Mixed Pydantic v1/v2 models now supported
- **Action Required**: Migrate all Pydantic v1 code to v2 if any exists

### Other Backend Updates

| Package | Old Version | New Version | Notes |
|---------|-------------|-------------|-------|
| uvicorn | 0.30.0 | 0.38.0 | Performance improvements |
| pydantic | 2.9.0 | 2.12.3 | Python 3.14 support |
| pydantic-settings | 2.5.0 | 2.11.0 | Compatible with pydantic 2.12 |
| httpx | 0.27.0 | 0.28.1 | Bug fixes |
| pandas | 2.2.2 | 2.3.0 | NumPy 2.x compatibility |
| matplotlib | 3.9.0 | 3.10.7 | Requires Python 3.10+ |
| python-multipart | 0.0.9 | 0.0.20 | Security updates |
| python-dotenv | 1.0.1 | 1.2.1 | Bug fixes |

## Frontend Updates (npm)

### Critical Updates

#### 1. **React: 18.3.1 → 19.2.0** 🔴 BREAKING
- **Major version update**
- New features: Actions, useOptimistic, useFormStatus
- TypeScript types updated
- **Action Required**:
  - Review [React 19 Upgrade Guide](https://react.dev/blog/2024/04/25/react-19-upgrade-guide)
  - Update TypeScript types: `@types/react@^19.2.2`, `@types/react-dom@^19.2.2`
  - Test all components

#### 2. **Vite: 5.3.1 → 7.1.12** 🔴 BREAKING
- **Two major versions jump** (5 → 6 → 7)
- Requires Node.js 20.19+ or 22.12+ (Node 18 dropped)
- New Environment API
- **Action Required**:
  - Update Node.js to 20.19+ or 22.12+
  - Review [Vite 6 migration](https://vite.dev/guide/migration)
  - Review [Vite 7 announcement](https://vite.dev/blog/announcing-vite7)

#### 3. **Tailwind CSS: v3 → v4** 🔴 BREAKING
- **Complete configuration change**
- No longer uses PostCSS (uses Lightning CSS)
- New Vite plugin: `@tailwindcss/vite`
- **Changes Made**:
  - ✅ Removed `tailwind.config.js` and `postcss.config.js`
  - ✅ Updated `vite.config.ts` to use `@tailwindcss/vite`
  - ✅ Updated `src/index.css`: `@import "tailwindcss";`
  - ❌ Removed `autoprefixer` and `postcss` (no longer needed)

#### 4. **ESLint: 8.57.0 → 9.38.0** 🟡 MINOR BREAKING
- New flat config system
- Some plugins may need updates
- **Action Required**: May need to update ESLint config

#### 5. **TypeScript: 5.5.3 → 5.9.3** 🟢 SAFE
- Minor version update
- New features and bug fixes
- No breaking changes expected

### Other Frontend Updates

| Package | Old Version | New Version | Notes |
|---------|-------------|-------------|-------|
| @vitejs/plugin-react | 4.3.1 | 5.1.0 | Vite 7 compatibility |
| @typescript-eslint/eslint-plugin | 7.13.1 | 8.18.2 | ESLint 9 support |
| @typescript-eslint/parser | 7.13.1 | 8.18.2 | ESLint 9 support |
| eslint-plugin-react-hooks | 4.6.2 | 5.1.0 | React 19 support |
| eslint-plugin-react-refresh | 0.4.7 | 0.4.16 | Bug fixes |

## Migration Steps

### Backend Migration

```bash
cd backend

# 1. Update dependencies
pip install -r requirements.txt

# 2. Test PydanticAI agents
python -m pytest tests/test_agents.py

# 3. Verify NumPy/Pandas compatibility
python -c "import numpy; import pandas; print(f'NumPy: {numpy.__version__}, Pandas: {pandas.__version__}')"

# 4. Run the application
python -m app.main
```

### Frontend Migration

```bash
cd frontend

# 1. Update Node.js (if needed)
node --version  # Should be 20.19+ or 22.12+

# 2. Clean install
rm -rf node_modules package-lock.json
npm install

# 3. Run dev server
npm run dev

# 4. Test build
npm run build
```

## Testing Checklist

### Backend
- [ ] All PydanticAI agents work correctly
- [ ] Router agent classifies intents properly
- [ ] Analysis agent queries data successfully
- [ ] Transform agent generates and executes pandas code
- [ ] Visualization agent creates charts
- [ ] Export agent saves files
- [ ] NumPy/Pandas operations work as expected
- [ ] No deprecation warnings

### Frontend
- [ ] App loads without errors
- [ ] File upload works
- [ ] Chat interface displays correctly
- [ ] Data preview renders
- [ ] Visualizations display
- [ ] Download links work
- [ ] Tailwind CSS styles apply correctly
- [ ] No console errors

## Rollback Plan

If issues occur, revert to previous versions:

### Backend Rollback
```bash
cd backend
git checkout HEAD~1 -- requirements.txt pyproject.toml
pip install -r requirements.txt
```

### Frontend Rollback
```bash
cd frontend
git checkout HEAD~1 -- package.json vite.config.ts src/index.css
git checkout HEAD -- tailwind.config.js postcss.config.js  # Restore if existed
npm install
```

## Known Issues

### PydanticAI v1.6.0
- API changes from 0.0.x series - review documentation
- Some tool decorators may have changed

### React 19
- Some third-party libraries may not be compatible yet
- Check component library compatibility (if using any)

### Vite 7
- Some plugins may need updates
- Watch for hot reload issues

### Tailwind CSS v4
- Custom plugins need migration
- Some v3 utilities may have changed
- Check for any custom Tailwind configurations

## References

- [FastAPI Release Notes](https://fastapi.tiangolo.com/release-notes/)
- [Pydantic Changelog](https://docs.pydantic.dev/latest/changelog/)
- [PydanticAI Changelog](https://ai.pydantic.dev/changelog/)
- [NumPy 2.0 Migration Guide](https://numpy.org/devdocs/numpy_2_0_migration_guide.html)
- [React 19 Upgrade Guide](https://react.dev/blog/2024/04/25/react-19-upgrade-guide)
- [Vite 7 Announcement](https://vite.dev/blog/announcing-vite7)
- [Tailwind CSS v4 Guide](https://tailwindcss.com/blog/tailwindcss-v4)

## Support

For issues related to package updates:
1. Check the migration guide above
2. Review package-specific changelogs
3. Create an issue in the repository with:
   - Package version
   - Error message
   - Steps to reproduce

---

**Updated**: October 27, 2025
**Python**: 3.12+
**Node.js**: 20.19+ or 22.12+
