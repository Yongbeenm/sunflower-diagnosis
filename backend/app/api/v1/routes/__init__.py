"""One module per resource: auth, users, diseases, symptoms, diagnosis,
feedback, admin_rbac, analytics, media.

Routers validate input, call a service, and shape the response. Nothing else.
One endpoint per resource action - never an /admin copy of a /doctor route.
"""
