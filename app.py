import hmac
import os
import math
from flask import Flask, jsonify, request
import storage


def create_app():
    app = Flask(__name__)
    storage.initialize()

    @app.before_request
    def require_key():
        if request.path == '/health':
            return None
        configured = os.environ.get('PIPELINE_API_KEY', '')
        provided = request.headers.get('X-API-Key', '')
        if not configured or not hmac.compare_digest(provided, configured):
            return jsonify(error='unauthorized'), 401

    @app.get('/health')
    def health():
        return jsonify(status='ok')

    @app.post('/events')
    def ingest():
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify(error='expected JSON object'), 400
        required = ('event_id', 'symbol', 'event_type', 'price')
        if any(key not in data for key in required):
            return jsonify(error='missing required fields'), 400
        if any(not isinstance(data[k], str) or not data[k].strip() or len(data[k]) > 100 for k in required[:3]):
            return jsonify(error='invalid text fields'), 400
        if type(data['price']) not in (int, float) or not math.isfinite(data['price']) or data['price'] <= 0:
            return jsonify(error='invalid price'), 400
        if data['event_type'] not in ('price_alert', 'risk_review'):
            return jsonify(error='unsupported event_type'), 400
        if not storage.create_event(data):
            return jsonify(error='duplicate event_id'), 409
        return jsonify(event=storage.get_event(data['event_id'])), 201

    @app.get('/events/<event_id>')
    def detail(event_id):
        event = storage.get_event(event_id)
        return (jsonify(event=event), 200) if event else (jsonify(error='not found'), 404)

    @app.post('/events/<event_id>/decision')
    def decision(event_id):
        data = request.get_json(silent=True)
        if not isinstance(data, dict) or data.get('decision') not in ('approved', 'rejected'):
            return jsonify(error='decision must be approved or rejected'), 400
        result = storage.decide(event_id, data['decision'])
        if result == 'missing':
            return jsonify(error='not found'), 404
        if result == 'conflict':
            return jsonify(error='event already decided'), 409
        return jsonify(event=storage.get_event(event_id))

    @app.get('/events/<event_id>/audit')
    def audit(event_id):
        if not storage.get_event(event_id):
            return jsonify(error='not found'), 404
        return jsonify(audit=storage.get_audit(event_id))

    return app


app = create_app()

if __name__ == '__main__':
    app.run(host=os.environ.get('BIND_HOST', '127.0.0.1'), port=5000)
