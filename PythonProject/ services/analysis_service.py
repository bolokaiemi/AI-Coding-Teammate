"""
Analysis Service

Handles storage and retrieval of AI code analysis results.

The actual intelligence will eventually live in:
    ai/code_analyzer.py
    ai/code_corrector.py
    ai/code_explainer.py
    ai/error_detector.py

This service is responsible for persistence and application logic.
"""

from datetime import datetime

from database.database import db
from database.models import Analysis, CodeSession


class AnalysisService:
    """Business logic for AI analysis results."""

    @staticmethod
    def get_analysis(analysis_id):
        """Return an analysis result by ID."""

        if not analysis_id:
            return None

        return db.session.get(
            Analysis,
            int(analysis_id)
        )

    @staticmethod
    def get_session_analyses(code_session_id):
        """Return all analyses for a code session."""

        return Analysis.query.filter_by(
            code_session_id=int(code_session_id)
        ).order_by(
            Analysis.created_at.desc()
        ).all()

    @staticmethod
    def get_latest_analysis(code_session_id):
        """Return the latest analysis for a code session."""

        return Analysis.query.filter_by(
            code_session_id=int(code_session_id)
        ).order_by(
            Analysis.created_at.desc()
        ).first()

    @staticmethod
    def create_analysis(
        code_session_id,
        analysis_type="code",
        status="completed",
        errors=None,
        warnings=None,
        suggestions=None,
        summary=None,
        explanation=None,
        original_code=None,
        corrected_code=None,
        correction_explanation=None,
        visual_data=None,
        code_flow=None,
        highlighted_lines=None,
        model_name=None,
        processing_time=None,
    ):
        """Create and persist an analysis result."""

        session = db.session.get(
            CodeSession,
            int(code_session_id)
        )

        if not session:
            raise ValueError("Code session not found.")

        errors = errors or []
        warnings = warnings or []
        suggestions = suggestions or []

        analysis = Analysis(
            code_session_id=session.id,
            analysis_type=analysis_type,
            status=status,
            error_count=len(errors),
            warning_count=len(warnings),
            errors=errors,
            warnings=warnings,
            suggestions=suggestions,
            summary=summary,
            explanation=explanation,
            original_code=original_code,
            corrected_code=corrected_code,
            correction_explanation=correction_explanation,
            visual_data=visual_data,
            code_flow=code_flow,
            highlighted_lines=highlighted_lines,
            model_name=model_name,
            processing_time=processing_time,
            completed_at=(
                datetime.utcnow()
                if status == "completed"
                else None
            ),
        )

        db.session.add(analysis)
        db.session.commit()

        return analysis

    @staticmethod
    def update_analysis(
        analysis_id,
        status=None,
        errors=None,
        warnings=None,
        suggestions=None,
        summary=None,
        explanation=None,
        corrected_code=None,
        correction_explanation=None,
        visual_data=None,
        code_flow=None,
        highlighted_lines=None,
        processing_time=None,
    ):
        """Update an existing analysis."""

        analysis = AnalysisService.get_analysis(
            analysis_id
        )

        if not analysis:
            raise ValueError("Analysis not found.")

        if status is not None:
            analysis.status = status

        if errors is not None:
            analysis.errors = errors
            analysis.error_count = len(errors)

        if warnings is not None:
            analysis.warnings = warnings
            analysis.warning_count = len(warnings)

        if suggestions is not None:
            analysis.suggestions = suggestions

        if summary is not None:
            analysis.summary = summary

        if explanation is not None:
            analysis.explanation = explanation

        if corrected_code is not None:
            analysis.corrected_code = corrected_code

        if correction_explanation is not None:
            analysis.correction_explanation = (
                correction_explanation
            )

        if visual_data is not None:
            analysis.visual_data = visual_data

        if code_flow is not None:
            analysis.code_flow = code_flow

        if highlighted_lines is not None:
            analysis.highlighted_lines = highlighted_lines

        if processing_time is not None:
            analysis.processing_time = processing_time

        if status == "completed":
            analysis.completed_at = datetime.utcnow()

        db.session.commit()

        return analysis

    @staticmethod
    def build_analysis_response(analysis):
        """Convert an analysis model into a frontend-friendly dictionary."""

        if not analysis:
            return None

        return {
            "id": analysis.id,
            "analysis_type": analysis.analysis_type,
            "status": analysis.status,
            "error_count": analysis.error_count,
            "warning_count": analysis.warning_count,
            "errors": analysis.errors or [],
            "warnings": analysis.warnings or [],
            "suggestions": analysis.suggestions or [],
            "summary": analysis.summary,
            "explanation": analysis.explanation,
            "original_code": analysis.original_code,
            "corrected_code": analysis.corrected_code,
            "correction_explanation": (
                analysis.correction_explanation
            ),
            "visual_data": analysis.visual_data,
            "code_flow": analysis.code_flow,
            "highlighted_lines": analysis.highlighted_lines,
            "model_name": analysis.model_name,
            "processing_time": analysis.processing_time,
        }

    @staticmethod
    def delete_analysis(analysis_id):
        """Delete an analysis result."""

        analysis = AnalysisService.get_analysis(
            analysis_id
        )

        if not analysis:
            raise ValueError("Analysis not found.")

        db.session.delete(analysis)
        db.session.commit()

        return True