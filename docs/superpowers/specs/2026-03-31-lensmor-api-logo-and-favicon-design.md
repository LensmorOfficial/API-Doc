# Lensmor API Logo and Favicon Design

Date: 2026-03-31

## Goal

Update the Mintlify documentation site in `API-Doc` so the site brand area shows the Lensmor logo beside the `Lensmor API` name, and the browser favicon uses the same logo.

## Scope

This effort includes:

- adding the shared Lensmor logo asset into the `API-Doc` repository
- updating Mintlify site configuration in `docs.json`
- using one SVG asset for both site logo and favicon

This effort does not include:

- adding a new public documentation page about brand assets
- changing API content pages such as `index.mdx` or `api-reference/**/*.mdx`
- introducing separate light and dark logo variants
- changing the application repo branding source file

## Source Asset Decision

The source of truth for the logo asset is the app repository file:

- `a60-lensmor-event-playground/public/assets/logo.svg`

That file will be copied into the docs repository as:

- `API-Doc/logo.svg`

The app repository file remains the upstream source for this asset. `API-Doc/logo.svg` is the published copy used by Mintlify, and future branding updates should be refreshed from the app repository source rather than edited independently in `API-Doc`.

## Mintlify Configuration Design

`docs.json` should be updated so Mintlify uses the same asset in both places:

- `logo.light = "/logo.svg"`
- `logo.dark = "/logo.svg"`
- `favicon = "/logo.svg"`

This keeps the branding configuration minimal and aligned with the current requirement: one shared logo across the scoped header branding and favicon.

## Approach Options Considered

### Option A: Add logo only, keep existing favicon

Pros:
- smallest visible change
- preserves current favicon file

Cons:
- two different brand assets remain in use
- docs branding can drift from the app branding source

### Option B: Use one shared logo for both header branding and favicon

Pros:
- simplest configuration
- one asset to maintain
- aligns docs and app branding immediately

Cons:
- favicon uses the shared logo icon asset, which may be less optimized than a favicon-specific asset

### Option C: Create separate docs-specific logo and favicon assets

Pros:
- maximum control for docs presentation

Cons:
- unnecessary for the current need
- creates extra asset maintenance work

## Recommendation

Use Option B.

It satisfies the immediate presentation goal with the fewest moving parts and no extra content changes.

## Planning Status

Planning-ready. No open design decisions remain for this scoped change.

## Expected Result

After the change:

- the Mintlify site brand area shows the Lensmor logo beside `Lensmor API`
- the browser tab favicon uses the same Lensmor logo asset
- `API-Doc` contains the static asset it needs to render the branding consistently

## Validation

After editing:

- `API-Doc/logo.svg` exists
- `docs.json` contains `logo.light`, `logo.dark`, and `favicon` pointing to `/logo.svg`
- running Mintlify locally should show the logo in the site chrome and the updated favicon in the browser tab
