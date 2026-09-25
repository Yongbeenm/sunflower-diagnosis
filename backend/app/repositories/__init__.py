"""Every database query in the project lives in this package.

Routers and services never write SQL or build select() statements themselves.
One module per aggregate: users, diseases, symptoms, diagnosis, feedback, rbac.
"""
