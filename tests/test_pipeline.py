import os
import tempfile
import unittest


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        os.environ['DATABASE_PATH'] = os.path.join(self.tmp.name, 'test.db')
        os.environ['PIPELINE_API_KEY'] = 'test-secret'
        from app import create_app
        self.client = create_app().test_client()
        self.headers = {'X-API-Key': 'test-secret'}
        self.payload = {'event_id': 'test-001', 'symbol': 'DEMO', 'event_type': 'price_alert', 'price': 42.5}

    def tearDown(self):
        self.tmp.cleanup()

    def test_authentication(self):
        self.assertEqual(self.client.post('/events', json=self.payload).status_code, 401)

    def test_ingestion_and_duplicate(self):
        self.assertEqual(self.client.post('/events', json=self.payload, headers=self.headers).status_code, 201)
        self.assertEqual(self.client.post('/events', json=self.payload, headers=self.headers).status_code, 409)

    def test_validation(self):
        invalid = dict(self.payload, price=-1)
        self.assertEqual(self.client.post('/events', json=invalid, headers=self.headers).status_code, 400)

    def test_decision_audit_and_reopen(self):
        self.client.post('/events', json=self.payload, headers=self.headers)
        url = '/events/test-001/decision'
        self.assertEqual(self.client.post(url, json={'decision': 'approved'}, headers=self.headers).status_code, 200)
        self.assertEqual(self.client.post(url, json={'decision': 'rejected'}, headers=self.headers).status_code, 409)
        self.assertEqual(len(self.client.get('/events/test-001/audit', headers=self.headers).json['audit']), 2)
        from app import create_app
        restarted = create_app().test_client()
        self.assertEqual(restarted.get('/events/test-001', headers=self.headers).json['event']['status'], 'approved')


if __name__ == '__main__':
    unittest.main()
