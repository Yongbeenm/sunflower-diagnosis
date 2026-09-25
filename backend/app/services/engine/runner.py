"""Diagnosis runner and persistence service.

This is the only module in the engine package allowed to interact with the database.
Connects the pure engine functions to repository loading and persistence.
"""

from __future__ import annotations

import uuid
from collections.abc import Mapping
from decimal import Decimal

from app.core.errors import NotFoundError
from app.models.auth import User
from app.models.diagnosis import (
    DiagnosisResult,
    DiagnosisSelectedSymptom,
    DiagnosisSession,
)
from app.models.enums import (
    DiagnosisAnswer,
    DiagnosisOutcome,
)
from app.models.ruleset import Ruleset
from app.repositories.diagnosis import DiagnosisRepository
from app.schemas.diagnosis import (
    AnswerType,
    DiagnosisRequest,
    DiagnosisResponse,
    DiagnosisResultDTO,
    DiagnosisSessionDetailResponse,
    DiagnosisSessionListResponse,
    DiagnosisSessionSummaryDTO,
    DiseaseRef,
    EvidenceDTO,
    EvidenceSymptomDTO,
    NextQuestionDTO,
    SelectedSymptomDTO,
)
from app.services.engine.explain import build_evidence
from app.services.engine.next_question import next_best_questions
from app.services.engine.scoring import (
    DiseaseRule,
    EngineParams,
    SymptomWeight,
    rank,
)


class DiagnosisRunner:
    """Orchestrates diagnosis rule evaluation, evidence building, and database persistence."""

    def __init__(self, repository: DiagnosisRepository) -> None:
        self.repository = repository

    async def _load_engine_context(
        self,
        locale: str,
    ) -> tuple[
        Ruleset,
        EngineParams,
        list[DiseaseRule],
        dict[int, str],
        dict[int, str],
    ]:
        """Fetch active ruleset and all published disease rules in a single batch query."""
        ruleset = await self.repository.get_active_ruleset()
        if ruleset is None:
            raise NotFoundError(detail="No active ruleset configured")

        params_dict = ruleset.params or {}
        params = EngineParams(
            lambda_absent=float(params_dict.get("lambda_absent", 0.5)),
            min_confidence=float(params_dict.get("min_confidence", 0.35)),
            pathognomonic_floor=float(params_dict.get("pathognomonic_floor", 0.85)),
            required_missing_penalty=float(params_dict.get("required_missing_penalty", 0.25)),
        )

        diseases = await self.repository.get_published_diseases_with_rules()
        disease_names = await self.repository.get_disease_names(locale=locale)
        symptom_code_map = await self.repository.get_symptom_code_map()

        disease_rules: list[DiseaseRule] = []
        for d in diseases:
            sweights: list[SymptomWeight] = []
            for ds in d.disease_symptoms:
                sweights.append(
                    SymptomWeight(
                        symptom_id=ds.symptom_id,
                        weight=float(ds.weight),
                        is_required=ds.is_required,
                        is_pathognomonic=ds.is_pathognomonic,
                    )
                )
                if ds.symptom and ds.symptom.code:
                    symptom_code_map[ds.symptom_id] = ds.symptom.code

            disease_rules.append(
                DiseaseRule(
                    disease_id=d.id,
                    slug=d.slug,
                    symptoms=tuple(sweights),
                )
            )

        return ruleset, params, disease_rules, disease_names, symptom_code_map

    def _evaluate(
        self,
        ruleset: Ruleset,
        params: EngineParams,
        rules: list[DiseaseRule],
        disease_names: dict[int, str],
        symptom_codes: dict[int, str],
        answers: Mapping[int, AnswerType],
        locale: str,
    ) -> tuple[
        DiagnosisOutcome,
        list[DiagnosisResultDTO],
        list[NextQuestionDTO],
        str | None,
    ]:
        """Pure evaluation generating ranked results, evidence, and next questions."""
        ranked_scores = rank(rules, answers, params)
        rule_map = {r.disease_id: r for r in rules}

        results: list[DiagnosisResultDTO] = []
        for i, score_item in enumerate(ranked_scores, start=1):
            rule = rule_map[score_item.disease_id]
            explanation = build_evidence(rule, answers)

            disease_name = disease_names.get(
                score_item.disease_id,
                score_item.slug.replace("-", " ").title(),
            )

            evidence_dto = EvidenceDTO(
                supporting=[
                    EvidenceSymptomDTO(
                        symptom=symptom_codes.get(item.symptom_id, str(item.symptom_id)),
                        weight=item.weight,
                    )
                    for item in explanation.supporting
                ],
                against=[
                    EvidenceSymptomDTO(
                        symptom=symptom_codes.get(item.symptom_id, str(item.symptom_id)),
                        weight=item.weight,
                    )
                    for item in explanation.against
                ],
                missing_key=[
                    EvidenceSymptomDTO(
                        symptom=symptom_codes.get(item.symptom_id, str(item.symptom_id)),
                        weight=item.weight,
                    )
                    for item in explanation.missing_key
                ],
            )

            results.append(
                DiagnosisResultDTO(
                    rank=i,
                    disease=DiseaseRef(
                        id=score_item.disease_id,
                        slug=score_item.slug,
                        name=disease_name,
                    ),
                    score=round(score_item.score, 3),
                    confidence=round(score_item.confidence, 3),
                    evidence=evidence_dto,
                )
            )

        next_questions_raw = next_best_questions(rules, answers, params, k=3)
        next_questions: list[NextQuestionDTO] = [
            NextQuestionDTO(
                symptom=symptom_codes.get(q.symptom_id, str(q.symptom_id)),
                information_gain=q.information_gain,
            )
            for q in next_questions_raw
        ]

        if results:
            outcome = DiagnosisOutcome.MATCHED
            feedback_prompt = None
        else:
            outcome = DiagnosisOutcome.NO_MATCH
            feedback_prompt = (
                "មិនមានជំងឺដែលត្រូវគ្នានឹងរោគសញ្ញាទាំងនេះទេ។ លោកអ្នកអាចផ្ញើមតិកែលម្អ ឬពិគ្រោះជាមួយអ្នកជំនាញកសិកម្ម។"
                if locale == "km"
                else (
                    "No matching disease identified with the observed symptoms. "
                    "You can submit feedback with crop photos or contact an "
                    "agronomist for guidance."
                )
            )

        return outcome, results, next_questions, feedback_prompt

    async def preview(self, req: DiagnosisRequest) -> DiagnosisResponse:
        """Stateless preview evaluation with zero database writes."""
        ruleset, params, rules, disease_names, symptom_codes = await self._load_engine_context(
            req.locale
        )
        outcome, results, next_questions, feedback_prompt = self._evaluate(
            ruleset=ruleset,
            params=params,
            rules=rules,
            disease_names=disease_names,
            symptom_codes=symptom_codes,
            answers=req.answers,
            locale=req.locale,
        )

        return DiagnosisResponse(
            session_id=None,
            ruleset_version=ruleset.version,
            outcome=outcome,
            results=results,
            next_best_questions=next_questions,
            feedback_prompt=feedback_prompt,
        )

    async def create_session(
        self,
        req: DiagnosisRequest,
        user: User | None,
    ) -> DiagnosisResponse:
        """Evaluate diagnosis and persist the session, selected symptoms, and ranked results."""
        ruleset, params, rules, disease_names, symptom_codes = await self._load_engine_context(
            req.locale
        )
        outcome, results, next_questions, feedback_prompt = self._evaluate(
            ruleset=ruleset,
            params=params,
            rules=rules,
            disease_names=disease_names,
            symptom_codes=symptom_codes,
            answers=req.answers,
            locale=req.locale,
        )

        session_id = uuid.uuid4()
        top_disease_id = results[0].disease.id if results else None
        top_confidence = Decimal(f"{results[0].confidence:.3f}") if results else None

        session = DiagnosisSession(
            id=session_id,
            user_id=user.id if user else None,
            ruleset_id=ruleset.id,
            locale=req.locale,
            symptom_count=len(req.answers),
            top_disease_id=top_disease_id,
            top_confidence=top_confidence,
            outcome=outcome,
        )

        # Selected symptoms
        for symptom_id, ans in req.answers.items():
            session.selected_symptoms.append(
                DiagnosisSelectedSymptom(
                    session_id=session_id,
                    symptom_id=symptom_id,
                    answer=DiagnosisAnswer(ans),
                )
            )

        # Ranked results with evidence JSONB snapshot
        for r in results:
            session.results.append(
                DiagnosisResult(
                    session_id=session_id,
                    rank=r.rank,
                    disease_id=r.disease.id,
                    disease_name_snapshot=r.disease.name,
                    score=Decimal(f"{r.score:.3f}"),
                    confidence=Decimal(f"{r.confidence:.3f}"),
                    evidence=r.evidence.model_dump(),
                )
            )

        await self.repository.save_session(session)

        return DiagnosisResponse(
            session_id=session.id,
            ruleset_version=ruleset.version,
            outcome=outcome,
            results=results,
            next_best_questions=next_questions,
            feedback_prompt=feedback_prompt,
        )

    async def get_history(
        self,
        user_id: int,
        page: int = 1,
        size: int = 20,
    ) -> DiagnosisSessionListResponse:
        """Fetch paginated history of diagnosis sessions for a grower."""
        sessions, total = await self.repository.get_user_sessions(
            user_id=user_id,
            page=page,
            size=size,
        )

        items: list[DiagnosisSessionSummaryDTO] = []
        for s in sessions:
            top_ref = None
            if s.top_disease:
                top_ref = DiseaseRef(
                    id=s.top_disease.id,
                    slug=s.top_disease.slug,
                    name=s.top_disease.slug.replace("-", " ").title(),
                )

            items.append(
                DiagnosisSessionSummaryDTO(
                    id=s.id,
                    created_at=s.created_at,
                    locale=s.locale,
                    symptom_count=s.symptom_count,
                    outcome=s.outcome,
                    top_disease=top_ref,
                    top_confidence=float(s.top_confidence)
                    if s.top_confidence is not None
                    else None,
                )
            )

        return DiagnosisSessionListResponse(
            items=items,
            total=total,
            page=page,
            size=size,
        )

    async def get_session(
        self,
        session_id: uuid.UUID,
        current_user: User,
    ) -> DiagnosisSessionDetailResponse:
        """Retrieve full details of a diagnosis session.

        Enforces privacy: non-owner without 'diagnosis:read_all' gets 404 (not 403),
        preventing session existence leaks.
        """
        session = await self.repository.get_session_by_id(session_id)
        if session is None:
            raise NotFoundError(detail="Diagnosis session not found")

        # Privacy check: must be owner or have diagnosis:read_all
        is_owner = session.user_id == current_user.id
        has_read_all = current_user.has_permission("diagnosis:read_all")

        if not is_owner and not has_read_all:
            # Do NOT leak existence with 403; raise 404
            raise NotFoundError(detail="Diagnosis session not found")

        # Reconstruct response DTO
        selected_symptoms: list[SelectedSymptomDTO] = []
        for sel in session.selected_symptoms:
            code = sel.symptom.code if sel.symptom else str(sel.symptom_id)
            selected_symptoms.append(
                SelectedSymptomDTO(
                    symptom_id=sel.symptom_id,
                    symptom_code=code,
                    answer=sel.answer,
                )
            )

        results_dto: list[DiagnosisResultDTO] = []
        for r in session.results:
            slug = r.disease.slug if r.disease else "unknown"
            results_dto.append(
                DiagnosisResultDTO(
                    rank=r.rank,
                    disease=DiseaseRef(
                        id=r.disease_id,
                        slug=slug,
                        name=r.disease_name_snapshot,
                    ),
                    score=float(r.score),
                    confidence=float(r.confidence),
                    evidence=EvidenceDTO.model_validate(r.evidence),
                )
            )

        feedback_prompt = None
        if session.outcome == DiagnosisOutcome.NO_MATCH:
            feedback_prompt = (
                "មិនមានជំងឺដែលត្រូវគ្នានឹងរោគសញ្ញាទាំងនេះទេ។ លោកអ្នកអាចផ្ញើមតិកែលម្អ ឬពិគ្រោះជាមួយអ្នកជំនាញកសិកម្ម។"
                if session.locale == "km"
                else (
                    "No matching disease identified with the observed symptoms. "
                    "You can submit feedback with crop photos or contact an "
                    "agronomist for guidance."
                )
            )

        return DiagnosisSessionDetailResponse(
            session_id=session.id,
            ruleset_version=session.ruleset.version if session.ruleset else "unknown",
            outcome=session.outcome,
            locale=session.locale,
            created_at=session.created_at,
            symptom_count=session.symptom_count,
            selected_symptoms=selected_symptoms,
            results=results_dto,
            next_best_questions=[],
            feedback_prompt=feedback_prompt,
        )
