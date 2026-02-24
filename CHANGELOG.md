# Changelog

All notable changes to Doors and Drawers will be documented in this file.

Format: [Semantic Versioning](https://semver.org/) — MAJOR.MINOR.PATCH

---

## [1.0.0] - 2026-02-24

### Added
- Initial release of Doors and Drawers order management system
- Customer management (create, edit, delete)
- Order and quote workflows with line items for doors and drawers
- Settings panels for door designs, styles, edge profiles, wood stock, panel types, panel rises, drawer pricing, and more
- PDF generation for quotes and orders (xhtml2pdf)
- HTMX-powered interactive UI with Tailwind CSS styling
- Waitress WSGI server with WhiteNoise static file serving
- cx_Freeze packaging for standalone Windows installer (MSI)
- SQLite database stored in %LOCALAPPDATA%\DoorsAndDrawers
- Auto-run migrations and seed defaults on startup
- Browser heartbeat monitor — server shuts down automatically when the browser tab is closed
- Centralized VERSION file used by launcher and installer
