# styles/

`index.css` holds `@import "tailwindcss"` plus the design tokens as CSS custom
properties on `:root`, redefined under `[data-theme="dark"]`.

Khmer needs a larger line-height than Latin: set it on `:lang(km)` and never
constrain text containers to a fixed height, or diacritics get clipped.
