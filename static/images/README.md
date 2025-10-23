# Logo Instructions

To add your Better For Y'all logo to the dashboard:

1. Save your logo file as `logo.png` (or `logo.svg` for best quality) in this directory
2. Recommended dimensions: 200px x 80px or similar horizontal format
3. The logo will automatically scale to 40px height in the navigation bar
4. Uncomment the logo line in `templates/base.html`:
   - Find line 14-15 in `templates/base.html`
   - Remove the `<!--` and `-->` comments around the `<img>` tag
   - If using a different file format (like .svg), update the filename in the src attribute

Example after uncommenting:
```html
<a href="{{ url_for('dashboard') }}" class="nav-brand">
    <img src="{{ url_for('static', filename='images/logo.png') }}" alt="Better For Y'all Logo" class="nav-logo">
    Better For Y'all Training
</a>
```

## Current Branding Colors

The dashboard uses the following color scheme (defined in `/static/css/style.css`):

- **Primary (Teal)**: #0d9488 - Energy & Health
- **Accent (Orange)**: #f97316 - Action & Motivation
- **Navy**: #1e293b - Professional & Trustworthy
- **Success (Green)**: #10b981
- **Danger (Red)**: #ef4444

To customize these colors, edit the `:root` CSS variables in `/static/css/style.css`.
