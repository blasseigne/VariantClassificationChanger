"""
Flask web application for the ACMG/AMP Variant Classification Advisor.
"""

from flask import Flask, render_template, request, jsonify

from ..evidence_codes import ALL_CODES, EvidenceDirection
from ..classifier import classify_from_names
from ..advisor import advise_from_names


app = Flask(__name__)


@app.route("/")
def index():
    """Render the main page with evidence code checkboxes."""
    pathogenic_codes = [
        c for c in ALL_CODES.values()
        if c.direction == EvidenceDirection.PATHOGENIC
    ]
    benign_codes = [
        c for c in ALL_CODES.values()
        if c.direction == EvidenceDirection.BENIGN
    ]
    return render_template(
        "index.html",
        pathogenic_codes=pathogenic_codes,
        benign_codes=benign_codes,
    )


@app.route("/api/classify", methods=["POST"])
def api_classify():
    """API endpoint: classify a variant from evidence codes."""
    data = request.get_json()
    if not data or "codes" not in data:
        return jsonify({"error": "Missing 'codes' field"}), 400

    code_names = data["codes"]
    if not isinstance(code_names, list):
        return jsonify({"error": "'codes' must be a list of strings"}), 400

    try:
        result = classify_from_names(code_names)
        return jsonify({
            "classification": result.classification.label,
            "short_label": result.classification.short_label,
            "total_points": result.total_points,
            "pathogenic_points": result.pathogenic_points,
            "benign_points": result.benign_points,
            "applied_codes": [c.code for c in result.applied_codes],
        })
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/advise", methods=["POST"])
def api_advise():
    """API endpoint: get upgrade/downgrade advice."""
    data = request.get_json()
    if not data or "codes" not in data:
        return jsonify({"error": "Missing 'codes' field"}), 400

    code_names = data["codes"]
    if not isinstance(code_names, list):
        return jsonify({"error": "'codes' must be a list of strings"}), 400

    max_codes = data.get("max_codes", 4)

    try:
        result = advise_from_names(code_names, max_codes=max_codes)

        def format_change(change):
            return {
                "target_tier": change.target_tier.label,
                "target_short": change.target_tier.short_label,
                "points_needed": change.points_needed,
                "options": [
                    {
                        "codes": [c.code for c in combo],
                        "descriptions": [c.description for c in combo],
                        "points": [c.points for c in combo],
                        "total_points": sum(c.points for c in combo),
                    }
                    for combo in change.possible_additions
                ],
            }

        return jsonify({
            "current_classification": result.current_classification.label,
            "current_short": result.current_classification.short_label,
            "total_points": result.total_points,
            "applied_codes": [c.code for c in result.applied_codes],
            "upgrades": [format_change(u) for u in result.upgrades],
            "downgrades": [format_change(d) for d in result.downgrades],
        })
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/codes", methods=["GET"])
def api_codes():
    """API endpoint: list all available evidence codes."""
    codes = []
    for c in ALL_CODES.values():
        codes.append({
            "code": c.code,
            "direction": c.direction.value,
            "strength": c.strength.value,
            "points": c.points,
            "description": c.description,
        })
    return jsonify({"codes": codes})


def create_app():
    """Factory function for creating the Flask app."""
    return app


if __name__ == "__main__":
    app.run(debug=True, port=8080)
