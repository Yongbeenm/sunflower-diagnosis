# features/

One vertical slice per feature. A slice owns its pages, components, hooks, and query
keys, and exports only what other slices actually need.

    auth/       login, register, AuthProvider, RequirePermission
    diseases/   library list, filters, disease detail
    diagnosis/  the symptom checker flow and the result view
    history/    the grower own past checks
    feedback/   report a problem, photo upload
    admin/      ONE admin console, gated per route by permission code

There is no separate `doctor/` slice. Agronomists and admins use the same admin
pages; the nav differs by permission, the pages do not.
