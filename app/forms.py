from flask_wtf import FlaskForm
from wtforms import FileField, HiddenField, PasswordField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, Regexp


def _strip(value):
    if isinstance(value, str):
        return value.strip()
    return value


class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6, max=128)])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Create account")


class LoginForm(FlaskForm):
    username_or_email = StringField(
        "Username or Email", validators=[DataRequired(), Length(max=120)]
    )
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log in")


class DiseaseBaseForm(FlaskForm):
    name_en = StringField(
        "Name (English)",
        validators=[DataRequired(), Length(max=120)],
        filters=[_strip],
    )
    name_km = StringField(
        "Name (Khmer)",
        validators=[DataRequired(), Length(max=120)],
        filters=[_strip],
    )
    cause_en = TextAreaField("Cause (English)", validators=[DataRequired()], filters=[_strip])
    cause_km = TextAreaField("Cause (Khmer)", validators=[DataRequired()], filters=[_strip])
    treatment_en = TextAreaField("Treatment (English)", validators=[DataRequired()], filters=[_strip])
    treatment_km = TextAreaField("Treatment (Khmer)", validators=[DataRequired()], filters=[_strip])
    prevention_en = TextAreaField("Prevention (English)", validators=[DataRequired()], filters=[_strip])
    prevention_km = TextAreaField("Prevention (Khmer)", validators=[DataRequired()], filters=[_strip])
    image = FileField("Replace image (PNG/JPG/WEBP)", validators=[Optional()])
    submit = SubmitField("Save changes")


class DiseaseCreateForm(DiseaseBaseForm):
    symptoms_en = TextAreaField("Symptoms (English)", validators=[DataRequired()], filters=[_strip])
    symptoms_km = TextAreaField("Symptoms (Khmer)", validators=[DataRequired()], filters=[_strip])


class DiseaseEditForm(DiseaseBaseForm):
    pass


class DiseaseSymptomsForm(FlaskForm):

    symptom_checklist_leaf = TextAreaField(
        "1) Leaf symptoms (one per line)",
        validators=[Optional()],
    )
    symptom_checklist_leaf_head = TextAreaField(
        "2) Leaf / Head symptoms (one per line)",
        validators=[Optional()],
    )
    symptom_checklist_whole_plant = TextAreaField(
        "3) Whole plant symptoms (one per line)",
        validators=[Optional()],
    )
    symptom_checklist_stem = TextAreaField(
        "4) Stem symptoms (one per line)",
        validators=[Optional()],
    )
    symptom_checklist_head = TextAreaField(
        "5) Head symptoms (one per line)",
        validators=[Optional()],
    )
    symptom_checklist_root = TextAreaField(
        "6) Root symptoms (one per line)",
        validators=[Optional()],
    )
    symptom_checklist_seedling = TextAreaField(
        "7) Seed / Seedling symptoms (one per line)",
        validators=[Optional()],
    )
    symptom_checklist_environment = TextAreaField(
        "8) Environment symptoms (one per line)",
        validators=[Optional()],
    )

    submit = SubmitField("Save symptom items")


class SymptomItemForm(FlaskForm):
    label_en = StringField(
        "Symptom label (English)",
        validators=[DataRequired(), Length(max=255)],
        filters=[_strip],
    )
    label_km = StringField(
        "Symptom label (Khmer)",
        validators=[DataRequired(), Length(max=255)],
        filters=[_strip],
    )
    category = SelectField("Symptom type", validators=[DataRequired()], choices=[])
    submit = SubmitField("Save symptom")


class GlobalSymptomForm(FlaskForm):
    old_label = HiddenField("Original label", validators=[DataRequired()])
    old_category = HiddenField("Original category", validators=[DataRequired()])
    label_en = StringField(
        "Symptom label (English)",
        validators=[DataRequired(), Length(max=255)],
        filters=[_strip],
    )
    label_km = StringField(
        "Symptom label (Khmer)",
        validators=[DataRequired(), Length(max=255)],
        filters=[_strip],
    )
    category = SelectField("Symptom type", validators=[DataRequired()], choices=[])
    disease_id = SelectField("Assign to disease", validators=[Optional()], choices=[])
    submit = SubmitField("Save symptom")


class GlobalSymptomCreateForm(FlaskForm):
    label_en = StringField(
        "Symptom label (English)",
        validators=[DataRequired(), Length(max=255)],
        filters=[_strip],
    )
    label_km = StringField(
        "Symptom label (Khmer)",
        validators=[DataRequired(), Length(max=255)],
        filters=[_strip],
    )
    category = SelectField("Symptom type", validators=[DataRequired()], choices=[])
    disease_id = SelectField("Assign to disease", validators=[Optional()], choices=[])
    submit = SubmitField("Add symptom")


class DiagnosisForm(FlaskForm):
    """CSRF-protected form wrapper for the symptom checker."""

    submit = SubmitField("Check Symptoms")


class ProfileForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=80)])

    current_password = PasswordField(
        "Current password (required to change username or password)", validators=[Optional()]
    )
    new_password = PasswordField(
        "New password", validators=[Optional(), Length(min=6, max=128)]
    )
    confirm_new_password = PasswordField(
        "Confirm new password", validators=[Optional(), EqualTo("new_password")]
    )

    submit = SubmitField("Save changes")


class AdminUserRoleForm(FlaskForm):
    role = SelectField("Role", validators=[DataRequired()], choices=[])
    submit = SubmitField("Save role")


class RoleCreateForm(FlaskForm):
    name = StringField(
        "Role name",
        validators=[
            DataRequired(),
            Length(min=2, max=50),
            Regexp(
                r"^[a-z0-9_-]+$",
                message="Use lowercase letters, numbers, dashes, or underscores only.",
            ),
        ],
    )
    description = StringField("Description", validators=[Optional(), Length(max=255)])
    submit = SubmitField("Create role")


class FeedbackForm(FlaskForm):
    symptom_check_id = HiddenField("Symptom check ID", validators=[Optional()])
    require_photo = HiddenField("Require photo", validators=[Optional()])
    subject = StringField("Subject", validators=[DataRequired(), Length(min=4, max=160)])
    message = TextAreaField("Message", validators=[DataRequired(), Length(min=10)])
    photo = FileField("Upload photo evidence (PNG/JPG/WEBP)", validators=[Optional()])
    submit = SubmitField("Send feedback")
