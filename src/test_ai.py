import unittest
from unittest.mock import patch, MagicMock
from ai_bricks.api import openai
import stats
import os

# Assuming the provided code is in a file named `ai_module.py`
from ai import use_key, set_user, complete, embedding, embeddings, get_token_count, get_community_usage_cost, \
    usage_stats


class TestAIModule(unittest.TestCase):

    @patch('ai_module.openai')
    def test_use_key(self, mock_openai):
        test_key = 'testkey123'
        use_key(test_key)
        mock_openai.use_key.assert_called_once_with(test_key)

    @patch('ai_module.stats')
    def test_set_user(self, mock_stats):
        test_user = 'testuser'
        set_user(test_user)
        mock_stats.get_stats.assert_called_once_with(user=test_user)
        # Check if the global variable is set
        self.assertIsNotNone(usage_stats)

    @patch('ai_module.openai')
    def test_complete(self, mock_openai):
        test_text = 'Hello, world!'
        mock_model = MagicMock()
        mock_openai.model.return_value = mock_model
        mock_model.complete.return_value = {'choices': [{'text': 'Hello, test!'}]}
        response = complete(test_text)
        self.assertIn('model', response)
        self.assertIn('text', response['choices'][0])

    @patch('ai_module.openai')
    def test_embedding(self, mock_openai):
        test_text = 'Hello, world!'
        mock_model = MagicMock()
        mock_openai.model.return_value = mock_model
        mock_model.embed.return_value = {'embedding': [0.1, 0.2, 0.3]}
        response = embedding(test_text)
        self.assertIn('model', response)
        self.assertIn('embedding', response)

    @patch('ai_module.openai')
    def test_embeddings(self, mock_openai):
        test_texts = ['Hello, world!', 'Goodbye, world!']
        mock_model = MagicMock()
        mock_openai.model.return_value = mock_model
        mock_model.embed_many.return_value = {'embeddings': [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]}
        response = embeddings(test_texts)
        self.assertIn('model', response)
        self.assertIn('embeddings', response)

    @patch('ai_module.tokenizer_model')
    def test_get_token_count(self, mock_tokenizer_model):
        test_text = 'Hello, world!'
        mock_tokenizer_model.token_count.return_value = 3
        token_count = get_token_count(test_text)
        self.assertEqual(token_count, 3)

    @patch('ai_module.usage_stats')
    def test_get_community_usage_cost(self, mock_usage_stats):
        mock_usage_stats.get.return_value = {
            'total_tokens:gpt-4': 1000,
            'total_tokens:text-davinci-003': 2000,
            'total_tokens:text-curie-001': 3000,
            'total_tokens:gpt-3.5-turbo': 4000,
            'total_tokens:text-embedding-ada-002': 5000,
        }
        cost = get_community_usage_cost()
        expected_cost = 0.04 + 0.04 + 0.006 + 0.008 + 0.002
        self.assertEqual(cost, expected_cost)

if __name__ == '__main__':
    unittest.main()

