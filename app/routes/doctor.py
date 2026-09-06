import json
import os
from datetime import datetime

from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from extensions import db
from app.forms import DiseaseCreateForm, DiseaseEditForm, GlobalSymptomCreateForm, GlobalSymptomForm, SymptomItemForm
from app.models.disease import Disease
from app.models.feedback import Feedback
from app.models.symptom_check import SymptomCheck
from app.services.disease_helpers import keyify, save_uploaded_image, slugify, unique_slug
from app.services.symptom_admin import (
    CHECKLIST_CATEGORY_CHOICES,
    SYSTEM_SYMPTOM_CATEGORY_CHOICES,
    add_symptom_to_disease,
    canonical_category,
    collect_all_symptoms,
    delete_catalog_symptom,
    disease_items,
    edit_catalog_symptom,
    delete_symptom_globally,
    edit_symptom_globally,
    ensure_catalog_symptom,
    ordered_checklist_groups,
    parse_symptoms_text_to_items,
    remove_symptom_from_disease,
    save_disease_items,
    sync_all_disease_symptom_data,
    sync_disease_symptom_data,
)
from app.utils import permission_required


doctor_bp = Blueprint("doctor", __name__, url_prefix="/doctor")


def _checklist_item_by_key(items: list[dict], item_key: str) -> dict | None:
    for item in items:
        if (item.get("key") or "").strip() == item_key:
            return item
    return None


def _global_symptom_row(diseases: list[Disease], *, label: str, category: str) -> dict | None:
    target_label = (label or "").strip().lower()
    target_category = (category or "").strip().lower()
    for row in collect_all_symptoms(diseases):
        if (row.get("label") or "").strip().lower() == target_label and (
            row.get("category") or ""
        ).strip().lower() == target_category:
            return row
    return None


def _system_symptom_disease_choices(
    diseases: list[Disease],
    *,
    empty_label: str,
    used_disease_names: list[str] | None = None,
) -> list[tuple[str, str]]:
    used_names = {name.strip() for name in (used_disease_names or []) if str(name).strip()}
    choices = [("", empty_label)]
    for disease in diseases:
        label = disease.name
        if disease.name in used_names:
            label = f"✓ {label}"
        choices.append((str(disease.id), label))
    return choices


def _selected_disease_ids_from_request() -> set[int]:
    selected: set[int] = set()
    for raw in request.form.getlist("disease_ids"):
        value = str(raw or "").strip()
        if value.isdigit():
            selected.add(int(value))
    return selected


def _system_symptom_assignment_diseases(
    diseases: list[Disease],
    *,
    selected_ids: set[int] | None = None,
    used_ids: set[int] | None = None,
) -> list[dict]:
    current = set(selected_ids or set())
    used = set(used_ids or set())
    rows = [
        {
            "id": disease.id,
            "name": disease.name,
            "selected": disease.id in current,
            "used": disease.id in used,
        }
        for disease in diseases
    ]
    return sorted(rows, key=lambda row: (not row["selected"], row["name"].lower()))


def _checklist_return_url(disease_id: int) -> str:
    if (request.values.get("next") or "").strip().lower() == "disease":
        return url_for("doctor.edit_disease", disease_id=disease_id)
    return url_for("doctor.edit_checklist", disease_id=disease_id)

@doctor_bp.route("/")
@login_required
@permission_required("manage_diseases")
def index():
    return redirect(url_for("doctor.dashboard"))


@doctor_bp.route("/dashboard")
@login_required
@permission_required("manage_diseases")
def dashboard():
    disease_count = Disease.query.count()
    recent_checks = SymptomCheck.query.order_by(SymptomCheck.created_at.desc()).limit(10).all()

    pending_reports = Disease.query.filter(
        (Disease.symptom_checklist_json == None)  # noqa: E711
        | (Disease.symptom_checklist_json == "")
        | (Disease.symptom_checklist_json == "[]")
    ).count()

    open_feedback = Feedback.query.filter_by(status="open").count()

    return render_template(
        "doctor/dashboard.html",
        disease_count=disease_count,
        pending_reports=pending_reports,
        recent_checks=recent_checks,
        open_feedback=open_feedback,
    )


@doctor_bp.route("/diseases")
@login_required
@permission_required("manage_diseases")
def diseases():
    diseases = Disease.query.order_by(Disease.name.asc()).all()
    changed = False
    for disease in diseases:
        if sync_disease_symptom_data(disease):
            changed = True
    if changed:
        db.session.commit()
    return render_template("doctor/diseases.html", diseases=diseases)


@doctor_bp.route("/checklists")
@login_required
@permission_required("manage_diseases")
def checklists():
    diseases = Disease.query.order_by(Disease.name.asc()).all()
    rows = []
    for disease in diseases:
        items = disease.checklist_items()
        symptom_labels = []
        for item in items:
            if isinstance(item, dict):
                label = (item.get("label") or "").strip()
            else:
                label = str(item).strip()
            if label:
                symptom_labels.append(label)

        rows.append(
            {
                "disease": disease,
                "symptom_labels": symptom_labels,
                "item_count": len(symptom_labels),
                "ready": bool(symptom_labels),
            }
        )

    return render_template("doctor/checklists.html", rows=rows)


@doctor_bp.route("/symptoms/all")
@login_required
@permission_required("manage_diseases")
def all_symptoms():
    diseases = Disease.query.order_by(Disease.name.asc()).all()
    if sync_all_disease_symptom_data(diseases):
        db.session.commit()
    symptoms = collect_all_symptoms(diseases)

    return render_template(
        "doctor/all_symptoms.html",
        symptoms=symptoms,
        diseases=diseases,
    )


@doctor_bp.route("/symptoms/all/add", methods=["GET", "POST"])
@login_required
@permission_required("manage_diseases")
def add_system_symptom():
    diseases = Disease.query.order_by(Disease.name.asc()).all()
    form = GlobalSymptomCreateForm()
    form.category.choices = SYSTEM_SYMPTOM_CATEGORY_CHOICES
    form.disease_id.choices = [("", "No disease yet")] + [
        (str(disease.id), disease.name) for disease in diseases
    ]

    if request.method == "GET":
        return render_template(
            "doctor/system_symptom_form.html",
            form=form,
            symptom=None,
            mode="add",
            assignment_diseases=[],
        )

    if not form.validate_on_submit():
        return render_template(
            "doctor/system_symptom_form.html",
            form=form,
            symptom=None,
            mode="add",
            assignment_diseases=[],
        )

    disease_id = int(form.disease_id.data) if (form.disease_id.data or "").strip() else None
    label = (form.label_en.data or "").strip()
    label_km = (form.label_km.data or "").strip()
    category = (form.category.data or "").strip()
    existing_symptom = _global_symptom_row(diseases, label=label, category=category)

    if existing_symptom is not None:
        if disease_id:
            disease = Disease.query.get_or_404(disease_id)
            changed = add_symptom_to_disease(
                disease,
                label=existing_symptom["label"],
                label_km=existing_symptom.get("label_km") or label_km or existing_symptom["label"],
                category=existing_symptom["category"],
            )
            if changed:
                disease.updated_by_id = current_user.id
                disease.updated_at = datetime.utcnow()
                db.session.commit()
                flash(
                    f'"{existing_symptom["label"]}" already exists in the system. Added it to {disease.name}.',
                    "success",
                )
                return redirect(url_for("doctor.all_symptoms"))

            flash("This symptom already exists for the selected disease.", "warning")
            return redirect(url_for("doctor.all_symptoms"))

        flash("This symptom already exists in the system.", "warning")
        return render_template(
            "doctor/system_symptom_form.html",
            form=form,
            symptom=existing_symptom,
            mode="add",
            assignment_diseases=[],
        )

    _, created = ensure_catalog_symptom(
        label=label,
        label_km=label_km,
        category=category,
        user_id=current_user.id,
    )
    flash_message = f'Symptom "{label}" created.'
    flash_category = "success" if created else "info"

    if disease_id:
        disease = Disease.query.get_or_404(disease_id)
        changed = add_symptom_to_disease(
            disease,
            label=label,
            label_km=label_km,
            category=category,
        )
        if changed:
            disease.updated_by_id = current_user.id
            disease.updated_at = datetime.utcnow()
            flash_message = f'Added "{label}" to {disease.name}.'
            flash_category = "success"
        else:
            flash_message = f'"{label}" already exists for {disease.name}. Symptom was kept in the system list.'
            flash_category = "info"

    db.session.commit()
    flash(flash_message, flash_category)
    return redirect(url_for("doctor.all_symptoms"))


@doctor_bp.route("/symptoms/all/edit", methods=["GET", "POST"])
@login_required
@permission_required("manage_diseases")
def edit_system_symptom():
    diseases = Disease.query.order_by(Disease.name.asc()).all()
    form = GlobalSymptomForm()
    form.category.choices = SYSTEM_SYMPTOM_CATEGORY_CHOICES
    form.disease_id.choices = _system_symptom_disease_choices(
        diseases,
        empty_label="Keep without disease",
    )

    if request.method == "GET":
        old_label = (request.args.get("label") or "").strip()
        old_category = (request.args.get("category") or "").strip()
        if not old_label or not old_category:
            flash("Symptom data is missing.", "danger")
            return redirect(url_for("doctor.all_symptoms"))

        symptom = _global_symptom_row(diseases, label=old_label, category=old_category)
        if symptom is None:
            abort(404)

        form.old_label.data = old_label
        form.old_category.data = old_category
        form.label_en.data = symptom["label"]
        form.label_km.data = symptom.get("label_km") or symptom["label"]
        form.category.data = symptom["category"]
        form.disease_id.data = ""
        current_ids = set(symptom.get("disease_ids") or [])

        return render_template(
            "doctor/system_symptom_form.html",
            form=form,
            symptom=symptom,
            mode="edit",
            assignment_diseases=_system_symptom_assignment_diseases(
                diseases,
                selected_ids=current_ids,
                used_ids=current_ids,
            ),
        )

    old_label = (form.old_label.data or "").strip()
    old_category = (form.old_category.data or "").strip()
    new_label = (form.label_en.data or "").strip()
    new_label_km = (form.label_km.data or "").strip()
    new_category = (form.category.data or "").strip()
    current_symptom = _global_symptom_row(diseases, label=old_label, category=old_category)
    current_ids = set((current_symptom or {}).get("disease_ids") or [])
    selected_ids = _selected_disease_ids_from_request() if request.method == "POST" else current_ids
    duplicate_target = _global_symptom_row(diseases, label=new_label, category=new_category)
    same_target = (
        (old_label or "").strip().lower() == new_label.lower()
        and canonical_category(old_category).lower() == canonical_category(new_category).lower()
    )

    if not form.validate_on_submit():
        symptom = current_symptom or {
            "label": old_label,
            "category": old_category,
            "label_km": old_label,
            "disease_count": 0,
            "disease_ids": [],
            "disease_names": [],
        }
        return render_template(
            "doctor/system_symptom_form.html",
            form=form,
            symptom=symptom,
            mode="edit",
            assignment_diseases=_system_symptom_assignment_diseases(
                diseases,
                selected_ids=selected_ids,
                used_ids=current_ids,
            ),
        )

    if duplicate_target is not None and not same_target:
        flash("This symptom already exists in the system.", "warning")
        symptom = current_symptom or {
            "label": old_label,
            "category": old_category,
            "label_km": old_label,
            "disease_count": 0,
            "disease_ids": [],
            "disease_names": [],
        }
        return render_template(
            "doctor/system_symptom_form.html",
            form=form,
            symptom=symptom,
            mode="edit",
            assignment_diseases=_system_symptom_assignment_diseases(
                diseases,
                selected_ids=selected_ids,
                used_ids=current_ids,
            ),
        )

    catalog_updates = edit_catalog_symptom(
        old_label=old_label,
        old_category=old_category,
        new_label=new_label,
        new_label_km=new_label_km,
        new_category=new_category,
        user_id=current_user.id,
    )

    affected_diseases, affected_items, changed_ids = edit_symptom_globally(
        diseases,
        old_label=old_label,
        old_category=old_category,
        new_label=new_label,
        new_label_km=new_label_km,
        new_category=new_category,
    )
    ensure_catalog_symptom(
        label=new_label,
        label_km=new_label_km,
        category=new_category,
        user_id=current_user.id,
    )

    added_names: list[str] = []
    removed_names: list[str] = []
    for disease in diseases:
        if disease.id in selected_ids and disease.id not in current_ids:
            if add_symptom_to_disease(
                disease,
                label=new_label,
                label_km=new_label_km,
                category=new_category,
            ):
                disease.updated_by_id = current_user.id
                disease.updated_at = datetime.utcnow()
                changed_ids.add(disease.id)
                added_names.append(disease.name)
        elif disease.id in current_ids and disease.id not in selected_ids:
            if remove_symptom_from_disease(
                disease,
                label=new_label,
                category=new_category,
            ):
                disease.updated_by_id = current_user.id
                disease.updated_at = datetime.utcnow()
                changed_ids.add(disease.id)
                removed_names.append(disease.name)

    if affected_items or catalog_updates or added_names or removed_names:
        now = datetime.utcnow()
        for disease in diseases:
            if disease.id in changed_ids:
                disease.updated_by_id = current_user.id
                disease.updated_at = now
        db.session.commit()
        details: list[str] = []
        if affected_items:
            details.append(f"updated in {affected_diseases} disease(s)")
        if added_names:
            details.append(f'added to {", ".join(added_names)}')
        if removed_names:
            details.append(f'removed from {", ".join(removed_names)}')
        flash(
            "Symptom updated" + (f" and {', '.join(details)}." if details else "."),
            "success",
        )
    else:
        db.session.rollback()
        flash("No matching symptom found to edit.", "warning")

    return redirect(url_for("doctor.all_symptoms"))


@doctor_bp.route("/symptoms/all/delete", methods=["POST"])
@login_required
@permission_required("manage_diseases")
def delete_system_symptom():
    label = (request.form.get("label") or "").strip()
    category = (request.form.get("category") or "").strip()
    if not label or not category:
        flash("Symptom data is missing.", "danger")
        return redirect(url_for("doctor.all_symptoms"))

    diseases = Disease.query.order_by(Disease.name.asc()).all()
    affected_diseases, removed_items, changed_ids = delete_symptom_globally(
        diseases,
        label=label,
        category=category,
    )
    removed_catalog = delete_catalog_symptom(label=label, category=category)
    if removed_items or removed_catalog:
        now = datetime.utcnow()
        for disease in diseases:
            if disease.id in changed_ids:
                disease.updated_by_id = current_user.id
                disease.updated_at = now
        db.session.commit()
        flash(
            f'Symptom removed from {affected_diseases} disease(s), {removed_items} item(s).',
            "info",
        )
    else:
        db.session.rollback()
        flash("No matching symptom found to delete.", "warning")

    return redirect(url_for("doctor.all_symptoms"))


@doctor_bp.route("/checklist/new", methods=["GET", "POST"])
@login_required
@permission_required("manage_diseases")
def new_checklist():
    disease_id = request.args.get("disease_id", type=int)
    if disease_id:
        return redirect(url_for("doctor.new_checklist_item", disease_id=disease_id))

    flash("Choose a disease from the Manage Symptoms list.", "info")
    return redirect(url_for("doctor.checklists"))


@doctor_bp.route("/checklist/<int:disease_id>/edit")
@login_required
@permission_required("manage_diseases")
def edit_checklist(disease_id: int):
    disease = Disease.query.get_or_404(disease_id)
    items = disease_items(disease)
    grouped_items = ordered_checklist_groups(items)
    category_counts = [
        {
            "category": label,
            "count": next(
                (group["count"] for group in grouped_items if group["category"] == label),
                0,
            ),
        }
        for label, _ in CHECKLIST_CATEGORY_CHOICES
    ]

    return render_template(
        "doctor/checklist_form.html",
        disease=disease,
        grouped_items=grouped_items,
        category_counts=category_counts,
        total_count=len(items),
    )


@doctor_bp.route("/checklist/<int:disease_id>/symptom/new", methods=["GET", "POST"])
@login_required
@permission_required("manage_diseases")
def new_checklist_item(disease_id: int):
    disease = Disease.query.get_or_404(disease_id)
    form = SymptomItemForm()
    form.category.choices = CHECKLIST_CATEGORY_CHOICES
    form.submit.label.text = "Add symptom"
    back_url = _checklist_return_url(disease.id)

    if form.validate_on_submit():
        changed = add_symptom_to_disease(
            disease,
            label=form.label_en.data,
            label_km=form.label_km.data,
            category=form.category.data,
        )
        if changed:
            disease.updated_by_id = current_user.id
            disease.updated_at = datetime.utcnow()
            db.session.commit()
            flash("Symptom added.", "success")
            return redirect(back_url)

        db.session.rollback()
        flash("This symptom already exists for this disease.", "warning")

    return render_template(
        "doctor/checklist_item_form.html",
        form=form,
        disease=disease,
        mode="add",
        item=None,
        back_url=back_url,
    )


@doctor_bp.route("/checklist/<int:disease_id>/symptom/<item_key>/edit", methods=["GET", "POST"])
@login_required
@permission_required("manage_diseases")
def edit_checklist_item(disease_id: int, item_key: str):
    disease = Disease.query.get_or_404(disease_id)
    items = disease_items(disease)
    item = _checklist_item_by_key(items, item_key)
    if item is None:
        abort(404)
    back_url = _checklist_return_url(disease.id)

    form = SymptomItemForm()
    form.category.choices = CHECKLIST_CATEGORY_CHOICES
    form.submit.label.text = "Save changes"

    if request.method == "GET":
        form.label_en.data = item["label"]
        form.label_km.data = item.get("label_km") or item["label"]
        form.category.data = item["category"]

    if form.validate_on_submit():
        new_label = (form.label_en.data or "").strip()
        new_label_km = (form.label_km.data or "").strip()
        new_category = (form.category.data or "").strip()
        duplicate = any(
            existing["key"] != item_key
            and (existing.get("label") or "").strip().lower() == new_label.lower()
            and (existing.get("category") or "").strip().lower() == new_category.lower()
            for existing in items
        )
        if duplicate:
            flash("This symptom already exists for this disease.", "warning")
        else:
            for existing in items:
                if existing["key"] == item_key:
                    existing["label"] = new_label
                    existing["label_km"] = new_label_km or new_label
                    existing["category"] = new_category
                    existing["key"] = keyify(new_label)
                    break

            save_disease_items(disease, items)
            disease.updated_by_id = current_user.id
            disease.updated_at = datetime.utcnow()
            db.session.commit()
            flash("Symptom updated.", "success")
            return redirect(back_url)

    return render_template(
        "doctor/checklist_item_form.html",
        form=form,
        disease=disease,
        mode="edit",
        item=item,
        back_url=back_url,
    )


@doctor_bp.route("/checklist/<int:disease_id>/symptom/<item_key>/delete", methods=["POST"])
@login_required
@permission_required("manage_diseases")
def delete_checklist_item(disease_id: int, item_key: str):
    disease = Disease.query.get_or_404(disease_id)
    items = disease_items(disease)
    remaining = [item for item in items if (item.get("key") or "").strip() != item_key]
    back_url = _checklist_return_url(disease.id)

    if len(remaining) == len(items):
        flash("Symptom item not found.", "warning")
        return redirect(back_url)

    save_disease_items(disease, remaining)
    disease.updated_by_id = current_user.id
    disease.updated_at = datetime.utcnow()
    db.session.commit()
    flash("Symptom deleted.", "info")
    return redirect(back_url)


@doctor_bp.route("/symptom-checks")
@login_required
@permission_required("view_symptom_checks")
def symptom_checks():
    checks = SymptomCheck.query.order_by(SymptomCheck.created_at.desc()).limit(200).all()
    return render_template("doctor/symptom_checks.html", checks=checks)


@doctor_bp.route("/symptom-check/<int:check_id>")
@login_required
@permission_required("view_symptom_checks")
def symptom_check_detail(check_id: int):
    check = SymptomCheck.query.get_or_404(check_id)

    parsed_results = []
    for r in check.results:
        try:
            matched = json.loads(r.matched_json) if r.matched_json else []
        except Exception:
            matched = []

        disease_id = r.disease_id
        if not disease_id and r.disease_key:
            disease_row = Disease.query.filter_by(slug=r.disease_key).first()
            disease_id = disease_row.id if disease_row else None

        parsed_results.append(
            {
                "rank": r.rank,
                "disease_id": disease_id,
                "disease_key": r.disease_key,
                "disease_name": r.disease_name,
                "percent": r.percent,
                "score": r.score,
                "matched": matched,
            }
        )

    return render_template(
        "doctor/symptom_check_detail.html",
        check=check,
        parsed_results=parsed_results,
    )


@doctor_bp.route("/feedback")
@login_required
@permission_required("manage_diseases")
def feedback():
    feedback_items = Feedback.query.order_by(Feedback.created_at.desc()).all()
    return render_template("doctor/feedback.html", feedback_items=feedback_items)


@doctor_bp.route("/feedback/<int:feedback_id>/resolve", methods=["POST"])
@login_required
@permission_required("manage_diseases")
def resolve_feedback(feedback_id: int):
    item = Feedback.query.get_or_404(feedback_id)
    if item.status != "resolved":
        item.status = "resolved"
        db.session.commit()
        flash("Feedback marked as resolved.", "success")
    return redirect(url_for("doctor.feedback"))


@doctor_bp.route("/disease/new", methods=["GET", "POST"])
@login_required
@permission_required("manage_diseases")
def new_disease():
    form = DiseaseCreateForm()
    form.submit.label.text = "Create disease"
    available_symptoms = collect_all_symptoms(Disease.query.order_by(Disease.name.asc()).all())

    if form.validate_on_submit():
        name_en = form.name_en.data.strip()
        symptoms_text_en = form.symptoms_en.data.strip()
        slug = unique_slug(Disease, slugify(name_en))

        disease = Disease(
            slug=slug,
            name=name_en,
            name_km=form.name_km.data.strip(),
            symptoms=symptoms_text_en,
            symptoms_km=form.symptoms_km.data.strip(),
            cause=form.cause_en.data.strip(),
            cause_km=form.cause_km.data.strip(),
            treatment=form.treatment_en.data.strip(),
            treatment_km=form.treatment_km.data.strip(),
            prevention=form.prevention_en.data.strip(),
            prevention_km=form.prevention_km.data.strip(),
            created_by_id=current_user.id,
            updated_by_id=current_user.id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        parsed_items = parse_symptoms_text_to_items(symptoms_text_en)
        save_disease_items(disease, parsed_items)

        if form.image.data:
            images_dir = os.path.join(current_app.root_path, "static", "images")
            try:
                stored = save_uploaded_image(
                    form.image.data,
                    images_dir=images_dir,
                    filename_prefix=slug,
                )
                disease.image_filename = stored
            except ValueError:
                flash("Image must be PNG/JPG/WEBP.", "danger")
                return render_template(
                    "doctor/new_disease.html",
                    form=form,
                    available_symptoms=available_symptoms,
                )

        db.session.add(disease)
        db.session.commit()

        flash(
            "Disease created. Symptoms were saved to the report and symptom checklist automatically.",
            "success",
        )
        return redirect(url_for("doctor.diseases"))
    elif request.method == "POST":
        flash("Please fill all required English and Khmer fields.", "danger")

    return render_template(
        "doctor/new_disease.html",
        form=form,
        available_symptoms=available_symptoms,
    )


@doctor_bp.route("/disease/<int:disease_id>/edit", methods=["GET", "POST"])
@login_required
@permission_required("manage_diseases")
def edit_disease(disease_id: int):
    disease = Disease.query.get_or_404(disease_id)
    form = DiseaseEditForm()
    grouped_items = ordered_checklist_groups(disease_items(disease))
    total_count = sum(group["count"] for group in grouped_items)

    if request.method == "GET":
        form.name_en.data = disease.name
        form.name_km.data = disease.name_km or ""
        form.cause_en.data = disease.cause
        form.cause_km.data = disease.cause_km or ""
        form.treatment_en.data = disease.treatment
        form.treatment_km.data = disease.treatment_km or ""
        form.prevention_en.data = disease.prevention
        form.prevention_km.data = disease.prevention_km or ""

    if form.validate_on_submit():
        disease.name = form.name_en.data.strip()
        disease.name_km = form.name_km.data.strip()
        disease.cause = form.cause_en.data.strip()
        disease.cause_km = form.cause_km.data.strip()
        disease.treatment = form.treatment_en.data.strip()
        disease.treatment_km = form.treatment_km.data.strip()
        disease.prevention = form.prevention_en.data.strip()
        disease.prevention_km = form.prevention_km.data.strip()
        disease.updated_by_id = current_user.id
        disease.updated_at = datetime.utcnow()

        if form.image.data:
            images_dir = os.path.join(current_app.root_path, "static", "images")
            try:
                stored = save_uploaded_image(
                    form.image.data,
                    images_dir=images_dir,
                    filename_prefix=disease.slug,
                )
                if stored:
                    disease.image_filename = stored
            except ValueError:
                flash("Image must be PNG/JPG/WEBP.", "danger")
                return render_template(
                    "doctor/edit_disease.html",
                    form=form,
                    disease=disease,
                    grouped_items=grouped_items,
                    total_count=total_count,
                )

        db.session.commit()

        flash("Disease updated.", "success")
        return redirect(url_for("doctor.diseases"))
    elif request.method == "POST":
        flash("Please fill all required English and Khmer fields.", "danger")

    return render_template(
        "doctor/edit_disease.html",
        form=form,
        disease=disease,
        grouped_items=grouped_items,
        total_count=total_count,
    )


@doctor_bp.route("/disease/<int:disease_id>/delete", methods=["POST"])
@login_required
@permission_required("delete_diseases")
def delete_disease(disease_id: int):
    disease = Disease.query.get_or_404(disease_id)

    if disease.image_filename:
        images_dir = os.path.join(current_app.root_path, "static", "images")
        img_path = os.path.join(images_dir, disease.image_filename)
        try:
            if os.path.exists(img_path):
                os.remove(img_path)
        except OSError:
            pass

    db.session.delete(disease)
    db.session.commit()
    flash("Disease deleted.", "info")
    return redirect(url_for("doctor.diseases"))
