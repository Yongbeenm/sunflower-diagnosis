# admin/

One console, permission-gated per route:

    /admin                  analytics:read
    /admin/diseases         disease:read
    /admin/diseases/new     disease:create
    /admin/diseases/:id     disease:update   (tabs: Content | Symptoms | Media)
    /admin/symptoms         symptom:read
    /admin/feedback         feedback:read
    /admin/users            user:manage
    /admin/roles            rbac:manage
    /admin/rulesets         ruleset:manage

The Symptoms tab of the disease editor is the most important screen in the product:
weight sliders, required / pathognomonic toggles, and a live preview that calls
POST /diagnosis/preview so a weight change is immediately legible.
