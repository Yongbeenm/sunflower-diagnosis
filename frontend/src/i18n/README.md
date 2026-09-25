# i18n/

react-i18next setup. Resources come from `../locales/en.json` and
`../locales/km.json`; the active locale is persisted and mirrored onto the `lang`
attribute of `<html>` so Khmer picks up Noto Sans Khmer.

Every user-facing string goes through `t("key")` and must exist in BOTH files.
Nested keys, grouped by feature: `diagnosis.checker.title`.
