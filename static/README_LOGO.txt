LOGO PLACEMENT INSTRUCTIONS
=============================

The dashboard uses three different logo placements with separate files:

1. Navbar Logo (Top Left)
   - Save as: "logo.png" in this static folder
   - Format: PNG with transparent background
   - Size: 700px width x 120px height (maximum)
   - Purpose: Navigation bar branding
   - Shows on: Dashboard pages only (Strategic, Operational, Analytical)

2. Homepage Main Logo (Center)
   - Save as: "main logo.png" in this static folder
   - Format: PNG with transparent background
   - Size: 1700px width x 350px height (maximum)
   - Purpose: Main homepage branding
   - Shows on: Homepage only

3. Olympic Logo (Bottom Section)
   - Save as: "olympic_logo.png" in this static folder
   - Format: PNG with transparent background
   - Size: 300px width x 80px height (maximum)
   - Purpose: Official Olympic branding
   - Shows on: Homepage bottom section

General Guidelines:
- Supported formats: PNG, JPG, JPEG, SVG
- Use transparent background when possible
- Logos will automatically scale while maintaining aspect ratio
- No fallback image shown if logo is missing
- For custom styling, edit CSS in templates/base.html

File Placement:
- Put all logo files in the /static directory:
  1. /static/logo.png (for navbar on dashboard pages)
  2. /static/main logo.png (for homepage main section)
  3. /static/olympic_logo.png (for homepage bottom section)

Note: The navbar will only appear on dashboard pages, not on the homepage.

For custom styling or different logo placement, edit the CSS in templates/base.html under the ".logo-placeholder", ".main-logo-placeholder", and ".olympic-logo-bottom" sections. 