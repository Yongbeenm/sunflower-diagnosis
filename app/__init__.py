import os

from flask import Flask, request

from config import Config
from extensions import csrf, db, login_manager, migrate


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    from app.services.i18n_store import init_i18n_databases, load_i18n_store

    # Ensure instance folder exists for runtime files.
    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)

    login_manager.init_app(app)
    csrf.init_app(app)

    # Blueprints
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.user import user_bp
    from app.routes.admin import admin_bp
    from app.routes.doctor import doctor_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(doctor_bp)

    @app.context_processor
    def inject_i18n_store():
        def role_label(role_name):
            labels = {
                "doctor": "Expert Sunflower",
                "admin": "Admin",
                "user": "User",
            }
            key = (role_name or "user").strip().lower()
            return labels.get(key, (role_name or "user").replace("_", " ").title())

        try:
            store = load_i18n_store()
        except Exception:
            store = {
                "en": {"ui": {}, "phrases": {}},
                "km": {"ui": {}, "phrases": {}},
            }
        lang = "km" if (request.cookies.get("sf-language") or "").strip().lower() == "km" else "en"
        return {"sf_i18n_store": store, "sf_lang": lang, "role_label": role_label}

    # Create tables + seed sample data on first run
    with app.app_context():
        init_i18n_databases()

        # Import models so SQLAlchemy registers them before create_all()
        from app.models import disease, feedback, i18n_message, rbac, symptom_catalog, symptom_check, user  # noqa: F401
        from app.services.schema_guard import ensure_schema_columns
        from app.services.seed import seed_if_empty

        db.create_all()
        ensure_schema_columns()
        seed_if_empty()

    return app
