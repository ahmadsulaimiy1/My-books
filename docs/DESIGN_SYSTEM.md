# Design System — Sultan Arabic AI

A flagship visual identity meant to sit alongside Vision 2030 publications, NEOM digital
interfaces, premium Qur'an apps, and executive government dashboards — not a typical
language-learning app's palette of playful primary colours and rounded mascots.

## Palette

Defined in `ui/theme/Color.kt` (Compose) and mirrored in `res/values/colors.xml` (XML surfaces
like the splash screen) — the two **must** stay numerically identical.

| Role | Colour | Hex |
|---|---|---|
| Primary | Royal Navy | `#082A66` |
| Primary (deep) | Royal Navy Deep | `#051A40` |
| Accent | Royal Gold | `#C9A961` |
| Accent (bright) | Royal Gold Bright | `#E4C77E` |
| Neutral | Platinum | `#E8E9EC` |
| Neutral | Silver | `#B9BDC7` |
| Semantic | Success / Warning / Error | `#2E9E6B` / `#CB8A2E` / `#B3413A` |

Rank tiers (`SultanColors.Tier*`) give each of the nine `ScholarRank` levels a distinct accent,
ascending in prestige — cooler, quieter tones for early ranks, gold tones for the top two.

### Contrast

Text/background pairs are checked against WCAG's relative-luminance contrast formula
(4.5:1 minimum for normal text, 3:1 for large text/UI components). The one pairing that failed
an audit pass — light theme's `onSecondary` on `secondary` — has been fixed:

| Pair | Ratio | Result |
|---|---|---|
| Royal Gold on Royal Navy Deep (dark theme primary) | ≈7.7:1 | Pass (AAA) |
| Silver on Royal Navy (dark theme body text) | ≈7.3:1 | Pass |
| Pure White on Royal Gold Dim (light theme, **previous** `onSecondary`) | ≈3.8:1 | **Fail** (below 4.5:1) |
| Ink Black on Royal Gold Dim (light theme, **current** `onSecondary`) | ≈5.25:1 | Pass |

If you introduce a new colour pairing, check it against this table's method before shipping —
white text reads as premium on navy but not on a mid-tone gold; dark text does.

## Typography

`ui/theme/Type.kt` defines the Material 3 type scale plus a dedicated `ArabicType` scale (larger
sizes, looser line-height) since Naskh-style Arabic script needs more vertical breathing room
than Latin text at the same visual weight. **Production note:** the current build uses system
font fallbacks (`FontFamily.Serif` / `FontFamily.Default`) — see the doc comment at the top of
`Type.kt`. Before shipping, bundle a licensed Arabic Naskh face (e.g. a proper Amiri/Noto Naskh
Arabic variant) and an editorial Latin serif under `res/font/` so typography stays fully offline
and on-brand; this scaffold intentionally avoids embedding third-party font binaries it doesn't
have redistribution rights to confirm.

## Shape & motion

- `ui/theme/Shape.kt` — generous corner radii (6dp–32dp across the Material scale), never sharp
  edges, never the small "app-store cartoon" pill shapes common in casual learning apps.
- `ui/theme/Motion.kt` — slower, more deliberate easing curves and durations than Material's
  defaults (`DurationStandard = 320ms`, `DurationEmphasized = 520ms`). Everything should feel
  weighted and considered, never bouncy.

## Dark mode is the flagship default

`SultanArabicAITheme` follows the system theme but is designed dark-first — executive
dashboards, premium fintech apps, and Qur'an apps all skew dark by default. Light mode
(`ui/theme/Theme.kt`'s `SultanLightColorScheme`) is a fully designed peer, not an inverted
afterthought: Platinum/White surfaces with Royal Navy text and Royal Gold (dimmed) accents.

## Iconography and symbolism

The eight-pointed star (khatim) monogram — built from two overlapping squares — is the flagship
seal motif, reused across the launcher icon (`res/drawable/ic_launcher_foreground.xml`) and the
certificate seal (`certificate/CertificateGenerator.kt`'s `drawSeal`). Keep this consistent
anywhere the brand needs a mark rather than the wordmark.

## Component language

`ui/components/Components.kt` holds the shared vocabulary:

- `StatCard` — executive-dashboard metric tile (value first, label second, a short gold rule as
  the accent) — the visual language for the Overview screen's analytics.
- `RankBadge` — the prestige-ladder progress indicator, tinted per rank tier.
- `SectionHeading` / `GoldDivider` — quiet section separators, never loud headers.

## What to avoid

No childish illustration, no confetti/emoji-driven gamification chrome, no generic
"educational app" green-and-blue palette, no cartoon mascots. Achievements and certificates use
the same restrained, editorial visual language as the rest of the app — a certificate should look
like something worth framing, not a game-over screen.
