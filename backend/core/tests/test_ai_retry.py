from unittest.mock import Mock, patch

from django.test import SimpleTestCase, override_settings
from requests.exceptions import Timeout

from core.ai_diagnosis import diagnose_crop_image
from core.ai_service import public_ai_error, run_ai_request


class AIRequestRetryTests(SimpleTestCase):
    @patch('core.ai_service.time.sleep')
    @patch('core.ai_diagnosis._diagnose_with_gemini')
    @override_settings(GEMINI_API_KEY='configured')
    def test_scan_recovers_from_provider_unavailability(self, diagnose, sleep):
        error = RuntimeError('provider unavailable')
        error.code = 503
        result = {'crop_name': 'cacao', 'is_valid_subject': True}
        diagnose.side_effect = [error, result]
        self.assertEqual(diagnose_crop_image(b'photo'), result)
        self.assertEqual(diagnose.call_count, 2)
        sleep.assert_called_once_with(1)

    @patch('core.ai_service.time.sleep')
    def test_timeout_recovers(self, sleep):
        request = Mock(side_effect=[Timeout('network timeout'), 'real result'])
        self.assertEqual(run_ai_request(request), 'real result')
        self.assertEqual(request.call_count, 2)

    @patch('core.ai_service.time.sleep')
    def test_persistent_failure_stops_after_one_retry(self, sleep):
        request = Mock(side_effect=Timeout('network timeout'))
        with self.assertRaises(Timeout):
            run_ai_request(request)
        self.assertEqual(request.call_count, 2)
        sleep.assert_called_once_with(1)

    @patch('core.ai_service.time.sleep')
    def test_quota_and_invalid_requests_are_not_retried(self, sleep):
        for code in (400, 401, 403, 429):
            with self.subTest(code=code):
                error = RuntimeError('permanent failure')
                error.code = code
                request = Mock(side_effect=error)
                with self.assertRaises(RuntimeError):
                    run_ai_request(request)
                request.assert_called_once()
        sleep.assert_not_called()

    def test_public_error_and_logs_never_expose_provider_message(self):
        error = RuntimeError('private-key-and-photo-data')
        with self.assertLogs('core.ai_service', level='ERROR') as logs:
            message, code = public_ai_error(error)
        self.assertEqual(code, 502)
        self.assertNotIn('private-key-and-photo-data', message)
        self.assertNotIn('private-key-and-photo-data', '\n'.join(logs.output))

    def test_daily_quota_message_does_not_promise_an_immediate_recovery(self):
        error = RuntimeError('private-provider-message')
        error.code = 429
        error.details = {'error': {'details': [{'violations': [
            {'quotaId': 'GenerateRequestsPerDayPerProjectPerModel-FreeTier', 'quotaValue': '20'},
        ]}]}}
        with self.assertLogs('core.ai_service') as logs:
            message, code = public_ai_error(error)
        self.assertEqual(code, 429)
        self.assertIn('quota quotidien', message)
        self.assertNotIn('private-provider-message', '\n'.join(logs.output))
